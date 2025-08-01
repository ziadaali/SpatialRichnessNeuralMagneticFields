import MEArec
from MEArec.tools import load_templates
from MEArec.generators import RecordingGenerator, SpikeTrainGenerator, TemplateGenerator
import yaml
import os
from distutils.version import StrictVersion
import time
from pathlib import Path
import numpy as np
import neo

if StrictVersion(yaml.__version__) >= StrictVersion('5.0.0'):
    use_loader = True
else:
    use_loader = False


def gen_recordings(params=None, templates=None, tempgen=None, spgen=None, verbose=True,
                   tmp_mode='memmap', template_ids=None, tmp_folder=None, n_jobs=0):
    """
    Generates recordings.

    Parameters
    ----------
    templates : str
        Path to generated templates
    params : dict or str
        Dictionary containing recording parameters OR path to yaml file containing parameters
    tempgen : TemplateGenerator
        Template generator object
    spgen : SpikeTrainGenerator
        Spike train generator object. If None spike trains are created from params['spiketrains']
    verbose: bool or int
        Determines the level of verbose. If 1 or True, low-level, if 2 high level, if False, not verbose
    tmp_mode : None, 'h5' 'memmap'
        Use temporary file h5 memmap or None
        None is no temporary file
    template_ids: list or None
        If None, templates are selected randomly based on selection rules. If a list of indices is provided, the
        indices are used to select templates (template selection is bypassed)
    tmp_folder: str or Path
        In case of tmp files, you can specify the folder.
        If None, then it is automatic using tempfile.mkdtemp()

    Returns
    -------
    RecordingGenerator
        Generated recording generator object
    """
    t_start = time.perf_counter()
    if isinstance(params, (str, Path)):
        params = Path(params)
        if params.is_file() and params.suffix in ['.yaml', '.yml']:
            with open(params, 'r') as pf:
                if use_loader:
                    params_dict = yaml.load(pf, Loader=yaml.FullLoader)
                else:
                    params_dict = yaml.load(pf)
    elif isinstance(params, dict):
        params_dict = params
    else:
        params_dict = {}

    if 'spiketrains' not in params_dict:
        params_dict['spiketrains'] = {}
    if 'templates' not in params_dict:
        params_dict['templates'] = {}
    if 'recordings' not in params_dict:
        params_dict['recordings'] = {}
    if 'cell_types' not in params_dict:
        params_dict['cell_types'] = {}
    if 'seeds' not in params_dict:
        params_dict['seeds'] = {}

    if tempgen is None and templates is None:
        raise AttributeError("Provide either 'templates' or 'tempgen' TemplateGenerator object")

    if tempgen is None:
        templates = Path(templates)
        if templates.is_dir():
            tempgen = load_templates(templates, verbose=False)
        elif templates.suffix in ['.h5', '.hdf5']:
            tempgen = load_templates(templates, verbose=False)
        else:
            raise AttributeError("'templates' is not a folder or an hdf5 file")

    if 'spiketrains' in params_dict['seeds']:
        if params_dict['seeds']['spiketrains'] is None:
            params_dict['seeds']['spiketrains'] = np.random.randint(1, 10000)
    else:
        params_dict['seeds']['spiketrains'] = np.random.randint(1, 10000)

    if 'templates' in params_dict['seeds']:
        if params_dict['seeds']['templates'] is None:
            params_dict['seeds']['templates'] = np.random.randint(1, 10000)
    else:
        params_dict['seeds']['templates'] = np.random.randint(1, 10000)

    if 'convolution' in params_dict['seeds']:
        if params_dict['seeds']['convolution'] is None:
            params_dict['seeds']['convolution'] = np.random.randint(1, 10000)
    else:
        params_dict['seeds']['convolution'] = np.random.randint(1, 10000)

    if 'noise' in params_dict['seeds']:
        if params_dict['seeds']['noise'] is None:
            params_dict['seeds']['noise'] = np.random.randint(1, 10000)
    else:
        params_dict['seeds']['noise'] = np.random.randint(1, 10000)

    # Generate spike trains
    if spgen is None:
        spgen = SpikeTrainGenerator(params_dict['spiketrains'], verbose=verbose,
                                    seed=params_dict['seeds']['spiketrains'])
        spgen.generate_spikes()
    else:
        assert isinstance(spgen, SpikeTrainGenerator), "'spgen' should be a SpikeTrainGenerator object"
        spgen.info['custom'] = True

    params_dict['spiketrains'] = spgen.info
    # Generate recordings
    recgen = RecordingGenerator(spgen, tempgen, params_dict)
    recgen.generate_recordings(tmp_mode=tmp_mode, tmp_folder=tmp_folder, template_ids=template_ids,
                               n_jobs=n_jobs, verbose=verbose)

    if verbose >= 1:
        print('Elapsed time: ', time.perf_counter() - t_start)

    return recgen


def gen_spiketrains(params=None, spiketrains=None, seed=None, verbose=False):
    """
    Generates spike trains.

    Parameters
    ----------
    params : str or dict
        Path to parameters yaml file or parameters dictionary
    spiketrains : list
        List of neo.SpikeTrains (alternative to params definition)
    verbose : bool
        If True, the output is verbose

    Returns
    -------
    SpikeTrainGenerator
        Generated spike train generator object
    """
    if params is None:
        assert spiketrains is not None, "Pass either a 'params' or a 'spiketrains' argument"
        assert isinstance(spiketrains, list) and isinstance(spiketrains[0], neo.SpikeTrain), \
            "'spiketrains' should be a list of neo.SpikeTrain objects"
        params_dict = {}
    else:
        if isinstance(params, (str, Path)):
            params = Path(params)
            if params.is_file() and params.suffix in ['.yaml', '.yml']:
                with open(params, 'r') as pf:
                    if use_loader:
                        params_dict = yaml.load(pf, Loader=yaml.FullLoader)
                    else:
                        params_dict = yaml.load(pf)
        elif isinstance(params, dict):
            params_dict = params
        else:
            params_dict = {}
        spiketrains = None

    spgen = SpikeTrainGenerator(params=params_dict, spiketrains=spiketrains, seed=seed, verbose=verbose)
    spgen.generate_spikes()

    return spgen


def gen_templates(cell_models_folder, params=None, templates_tmp_folder=None, tempgen=None,
                  intraonly=False, parallel=True, n_jobs=None, joblib_backend="loky",
                  recompile=False, delete_tmp=True, verbose=True):
    """

    Parameters
    ----------
    cell_models_folder : str
        path to folder containing cell models
    params : str or dict
        Path to parameters yaml file or parameters dictionary
    templates_tmp_folder: str
        Path to temporary folder where templates are temporarily saved
    tempgen :  TemplateGenerator
        If a TemplateGenerator is passed, the cell types, locations, and rotations of the templates will be set using
        the provided templates
    intraonly : bool
        if True, only intracellular simulation is run
    parallel : bool
        if True, multi-threading is used
    n_jobs: int
        Number of jobs to run in parallel (If None all cpus are used)
    joblib_backend: str
        The joblib backend to use when n_jobs > 1 (default 'loky')
    recompile: bool
        If True, cell models are recompiled
    delete_tmp :
        if True, the temporary files are deleted
    verbose : bool
        If True, the output is verbose

    Returns
    -------
    TemplateGenerator
        Generated template generator object

    """
    if isinstance(params, (str, Path)):
        params = Path(params)
        if params.is_file() and params.suffix in ['.yaml', '.yml']:
            with open(params, 'r') as pf:
                if use_loader:
                    params_dict = yaml.load(pf, Loader=yaml.FullLoader)
                else:
                    params_dict = yaml.load(pf)
    elif isinstance(params, dict):
        params_dict = params
    else:
        params_dict = None

    if tempgen is not None:
        if isinstance(tempgen, (str, Path)):
            tempgen_arg = load_templates(tempgen)
        else:
            assert isinstance(tempgen, TemplateGenerator), \
                "'tempgen' should be a TemplateGenerator"
            tempgen_arg = tempgen
    else:
        tempgen_arg = tempgen

    if templates_tmp_folder is not None:
        if not Path(templates_tmp_folder).is_dir():
            os.makedirs(templates_tmp_folder)

    tempgen = TemplateGenerator(cell_models_folder=cell_models_folder,
                                params=params_dict,
                                templates_folder=templates_tmp_folder,
                                tempgen=tempgen_arg,
                                intraonly=intraonly,
                                parallel=parallel,
                                recompile=recompile,
                                n_jobs=n_jobs,
                                joblib_backend=joblib_backend,
                                delete_tmp=delete_tmp,
                                verbose=verbose)
    tempgen.generate_templates()

    return tempgen
