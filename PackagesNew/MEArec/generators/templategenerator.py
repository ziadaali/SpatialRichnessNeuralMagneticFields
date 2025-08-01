import time
import numpy as np
from MEArec.tools import *
import MEAutility as mu
import shutil
import yaml
import os
from distutils.version import StrictVersion
from pathlib import Path
from joblib import Parallel, delayed, cpu_count
from MEArec.simulate_cells import compute_eap_for_cell_model, compute_eap_based_on_tempgen

if StrictVersion(yaml.__version__) >= StrictVersion('5.0.0'):
    use_loader = True
else:
    use_loader = False


def simulate_cell_templates(i, simulate_script, tot, cell_model,
                            model_folder, intraonly, params, verbose):
    model_folder = Path(model_folder)
    print(f"Starting {i + 1}")
    print(f'\n\n {cell_model} {i + 1}/{tot}\n\n')
    os.system(f'python {simulate_script} {str(model_folder / cell_model)} {intraonly} {params} {verbose}')
    print(f"Exiting {i + 1}")


class TemplateGenerator:
    """
    Class for generation of templates called by the gen_templates function.
    The list of parameters is in default_params/templates_params.yaml.

    Parameters
    ----------
    cell_models_folder : str
        Path to folder containing Blue Brain Project cell models
    templates_folder : str
        Path to output template folder (if not in params)
    temp_dict :  dict
        Dictionary to instantiate TemplateGenerator with existing data. It contains the following fields:
          - templates : float (n_templates, n_electrodes, n_timepoints)
          - locations : float (n_templates, 3)
          - rotations : float (n_templates, 3)
          - celltypes : str (n_templates)
    info :  dict
        Info dictionary to instantiate TemplateGenerator with existing data. It contains the following fields:
          - params : dict with template generation parameters
          - electrodes : dict with probe info (from MEAutility.return_mea_info('probe-name'))
    tempgen : TemplateGenerator
        If a TemplateGenerator is passed, the cell types, locations, and rotations of the templates will be set using
        the provided templates
    params : dict
        Dictionary with parameters to simulate templates. Default values can be retrieved with
        mr.get_default_template_params()
    intraonly : bool
        If True, only intracellular simulations are performed
    parallel : bool
        If True, cell models are run in parallel
    recompile: bool
        If True, cell models are recompiled (suggested if new models are added)
    n_jobs: int
        If None, all cpus are used
    delete_tmp : bool
        If True, temporary files are removed
    verbose : bool
        If True, output is verbose
    """

    def __init__(self, cell_models_folder=None, templates_folder=None, temp_dict=None, info=None, tempgen=None,
                 params=None, intraonly=False, parallel=True, recompile=False, n_jobs=None,
                 joblib_backend="loky", delete_tmp=True,
                 verbose=False):
        self._verbose = verbose
        if temp_dict is not None and info is not None:
            if 'templates' in temp_dict.keys():
                self.templates = temp_dict['templates']
            if 'locations' in temp_dict.keys():
                self.locations = temp_dict['locations']
            if 'rotations' in temp_dict.keys():
                self.rotations = temp_dict['rotations']
            if 'celltypes' in temp_dict.keys():
                self.celltypes = temp_dict['celltypes']
            self.info = info
            self.params = deepcopy(info)
        else:
            if cell_models_folder is None:
                raise AttributeError("Specify cell folder!")
            if params is None:
                if self._verbose:
                    print("Using default parameters")
                self.params = {}
            else:
                self.params = deepcopy(params)
            self.cell_model_folder = Path(cell_models_folder)
            self.n_jobs = n_jobs
            self.joblib_backend = joblib_backend
            if templates_folder is not None:
                templates_folder = Path(templates_folder)
            self.templates_folder = templates_folder
            self.tempgen = tempgen
            self.simulation_params = {'intraonly': intraonly, 'parallel': parallel, 'delete_tmp': delete_tmp,
                                      'recompile': recompile}

    def generate_templates(self):
        """
        Generate templates.
        """
        cell_models_folder = self.cell_model_folder
        templates_folder = self.templates_folder
        intraonly = self.simulation_params['intraonly']
        parallel = self.simulation_params['parallel']
        recompile = self.simulation_params['recompile']
        delete_tmp = self.simulation_params['delete_tmp']

        if cell_models_folder.is_dir():
            cell_models = [f for f in cell_models_folder.iterdir() if 'mods' not in f.name
                           and not f.name.startswith('.')]
            if len(cell_models) == 0:
                raise AttributeError(cell_models_folder, ' contains no cell models!')
        else:
            raise NotADirectoryError('Cell models folder: does not exist!')

        this_dir, this_filename = os.path.split(__file__)
        simulate_script = str(Path(this_dir).parent / 'simulate_cells.py')

        # Compile NEURON models (nrnivmodl)
        if not (cell_models_folder / 'mods').is_dir() or recompile:
            if self._verbose:
                print('Compiling NEURON models')
            os.system(f'python {simulate_script} compile {cell_models_folder}')

        # sort cell model names
        cell_models = np.array(cell_models)[np.argsort([f.name for f in cell_models])]

        if 'sim_time' not in self.params.keys():
            self.params['sim_time'] = 1
        if 'target_spikes' not in self.params.keys():
            self.params['target_spikes'] = [3, 50]
        if 'cut_out' not in self.params.keys():
            self.params['cut_out'] = [2, 5]
        if 'dt' not in self.params.keys():
            self.params['dt'] = 2 ** -5
        if 'delay' not in self.params.keys():
            self.params['delay'] = 10
        if 'weights' not in self.params.keys():
            self.params['weights'] = [0.25, 1.75]

        if 'rot' not in self.params.keys():
            self.params['rot'] = 'physrot'
        if 'probe' not in self.params.keys():
            available_mea = mu.return_mea_list()
            probe = available_mea[np.random.randint(len(available_mea))]
            if self._verbose:
                print("Probe randomly set to: %s" % probe)
            self.params['probe'] = probe
        if 'ncontacts' not in self.params.keys():
            self.params['ncontacts'] = 1
        if 'overhang' not in self.params.keys():
            self.params['overhang'] = 1
        if 'xlim' not in self.params.keys():
            self.params['xlim'] = [10, 80]
        if 'ylim' not in self.params.keys():
            self.params['ylim'] = None
        if 'zlim' not in self.params.keys():
            self.params['zlim'] = None
        if 'offset' not in self.params.keys():
            self.params['offset'] = 0
        if 'det_thresh' not in self.params.keys():
            self.params['det_thresh'] = 30
        if 'n' not in self.params.keys():
            self.params['n'] = 50
        if 'min_amp' not in self.params.keys():
            self.params['min_amp'] = 30
        if 'seed' not in self.params.keys():
            self.params['seed'] = np.random.randint(1, 10000)
        elif self.params['seed'] is None:
            self.params['seed'] = np.random.randint(1, 10000)
        if templates_folder is None:
            info, _ = get_default_config()
            self.params['templates_folder'] = info['templates_folder']
            templates_folder = Path(self.params['templates_folder'])
        else:
            self.params['templates_folder'] = str(templates_folder)
        self.params['cell_models_folder'] = str(cell_models_folder)
        if 'drifting' not in self.params.keys():
            self.params['drifting'] = False
        if 'max_drift' not in self.params.keys():
            self.params['max_drift'] = 100
        if 'min_drift' not in self.params.keys():
            self.params['min_drift'] = 30
        if 'drift_steps' not in self.params.keys():
            self.params['drift_steps'] = 10
        if 'drift_xlim' not in self.params.keys():
            self.params['drift_xlim'] = [-10, 10]
        if 'drift_ylim' not in self.params.keys():
            self.params['drift_ylim'] = [-10, 10]
        if 'drift_zlim' not in self.params.keys():
            self.params['drift_zlim'] = [20, 80]
        if 'check_for_drift_amp' not in self.params.keys():
            self.params['check_for_drift_amp'] = False
        if 'drift_within_bounds' not in self.params.keys():
            self.params['drift_within_bounds'] = False

        rot = self.params['rot']
        n = self.params['n']
        probe = self.params['probe']

        tmp_params_path = 'tmp_params_path.yaml'
        with open(tmp_params_path, 'w') as f:
            yaml.dump(self.params, f)

        if self.tempgen is not None and parallel and self.n_jobs not in (0, 1):
            print("\nWARNING: Generation of templates from a template generator is only supported without parallel "
                  "processing. Setting parallel to False\n")
            parallel = False

        # Simulate neurons and EAP for different cell models separately
        if parallel and self.n_jobs not in (0, 1):
            start_time = time.time()
            tot = len(cell_models)
            if self.n_jobs is None:
                n_jobs = cpu_count()
                print(f"Setting n_jobs to {n_jobs} CPUs")
            else:
                n_jobs = self.n_jobs

            if self._verbose:
                print('Running with', n_jobs, 'jobs')

            Parallel(n_jobs=n_jobs, backend=self.joblib_backend)(
                delayed(simulate_cell_templates)(i, simulate_script, tot, cell_model,
                                                 cell_models_folder, intraonly, tmp_params_path,
                                                 self._verbose, )
                for i, cell_model in enumerate(cell_models))
        else:
            start_time = time.time()
            if self.tempgen is None:
                for numb, cell_model in enumerate(cell_models):
                    if self._verbose:
                        print(f'\n\n {cell_model} {numb + 1}/{len(cell_models)}\n\n')
                    compute_eap_for_cell_model(cell_model=cell_models_folder / cell_model, params_path=tmp_params_path,
                                               intraonly=intraonly, verbose=self._verbose)

            else:
                print("Using template generation info")
                compute_eap_based_on_tempgen(cell_folder=cell_models_folder,
                                             params_path=tmp_params_path,
                                             tempgen=self.tempgen,
                                             intraonly=intraonly,
                                             verbose=self._verbose)

        tmp_folder = Path(templates_folder) / rot / f'tmp_{n}_{probe}'

        if not Path(tmp_folder).is_dir():
            raise FileNotFoundError(
                f'{tmp_folder} not found. Something went wrong in the template generation phase.')

        templates, locations, rotations, celltypes = load_tmp_eap(tmp_folder)
        if delete_tmp:
            shutil.rmtree(tmp_folder)
            os.remove(tmp_params_path)

        self.info = {}

        self.templates = templates
        self.locations = locations
        self.rotations = rotations
        self.celltypes = celltypes

        self.info['params'] = self.params
        self.info['electrodes'] = mu.return_mea_info(probe)

        print(f'\n\n\nSimulation time: {time.time() - start_time}\n\n\n')
