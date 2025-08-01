import os
import pprint
import time
from distutils.version import StrictVersion
from pathlib import Path

import MEArec.generation_tools as gt
import MEAutility as mu
import click
import numpy as np
import yaml
from MEArec import save_template_generator, save_recording_generator, get_default_config

if StrictVersion(yaml.__version__) >= StrictVersion('5.0.0'):
    use_loader = True
else:
    use_loader = False


@click.group()
def cli():
    """MEArec: Fast and customizable simulation of extracellular recordings on Multi-Electrode-Arrays """
    pass


@cli.command()
@click.option('--params', '-prm', default=None,
              help='path to default_params.yaml (otherwise default default_params are used and some of the parameters'
                   'can be overwritten with the following options)')
@click.option('--default', is_flag=True,
              help='shows default values for simulation')
@click.option('--fname', '-fn', default=None,
              help='template filename')
@click.option('--folder', '-fol', default=None,
              help='templates output base folder')
@click.option('--cellfolder', '-cf', default=None,
              help='folder containing bbp cell models')
@click.option('--rot', '-r', default=None,
              help='possible rotation arguments: norot-xrot-yrot-zrot-physrot-3drot (default=physrot)')
@click.option('--probe', '-prb', default=None,
              help='probe name from available electrodes (default=None)')
@click.option('--n', '-n', default=None, type=int,
              help='number of observations per cell type (default=50)')
@click.option('--njobs', '-nj', default=None, type=int,
              help='number of jobs (default n_jobs=n_cpus)')
@click.option('--dt', '-dt', default=None, type=float,
              help='time period in ms (default=0.03125)')
@click.option('--ncontacts', '-nc', default=None, type=int,
              help='number of contacts per electrode (default=1)')
@click.option('--overhang', '-ov', default=None, type=float,
              help='extension (um) beyond MEA boundaries for neuron locations (default=30.)')
@click.option('--xlim', '-xl', default=None, nargs=2, type=float,
              help='limits ( low high ) for neuron locations in the x-axis (depth) (default=[10.,80.])')
@click.option('--ylim', '-yl', default=None, nargs=2, type=float,
              help='limits ( low high ) for neuron locations in the y-axis (default=None)')
@click.option('--zlim', '-zl', default=None, nargs=2, type=float,
              help='limits ( low high ) for neuron locations in the z-axis (default=None)')
@click.option('--seed', '-s', default=None, type=int,
              help='random seed for template generation (int)')
@click.option('--intraonly', '-io', is_flag=True,
              help='only run intracellular simulations')
@click.option('--no-parallel', '-nopar', is_flag=True,
              help='run without multiprocessing tool')
@click.option('--recompile', '-rc', is_flag=True,
              help='recompile models')
@click.option('--drifting', '-dr', is_flag=True,
              help='generate drifting templates')
@click.option('--min-amp', '-mamp', type=float,
              help='miniumum template amplitude')
@click.option('--min-drift', '-mind', type=float,
              help='miniumum drifting distance')
@click.option('--max-drift', '-maxd', type=float,
              help='maximum drifting distance')
@click.option('--drift-steps', '-drst', type=int,
              help='number of drift steps')
@click.option('--drift-xlim', '-dxl', default=None, nargs=2, type=float,
              help='limits ( low high ) for neuron drift locations in the x-axis (depth) (default=[10.,80.])')
@click.option('--drift-ylim', '-dyl', default=None, nargs=2, type=float,
              help='limits ( low high ) for neuron drift locations in the y-axis (default=None)')
@click.option('--drift-zlim', '-dzl', default=None, nargs=2, type=float,
              help='limits ( low high ) for neuron drift locations in the z-axis (default=None)')
@click.option('--verbose', '-v', is_flag=True,
              help='produce verbose output')
def gen_templates(params, **kwargs):
    """Generates TEMPLATES with biophysical simulation."""
    info, config_folder = get_default_config()

    if params is None:
        with open(info['templates_params'], 'r') as pf:
            if use_loader:
                params_dict = yaml.load(pf, Loader=yaml.FullLoader)
            else:
                params_dict = yaml.load(pf)
    else:
        with open(params, 'r') as pf:
            if use_loader:
                params_dict = yaml.load(pf, Loader=yaml.FullLoader)
            else:
                params_dict = yaml.load(pf)

    if kwargs['default'] is True:
        pprint.pprint(params_dict)
        mu.return_mea()
        return

    if kwargs['cellfolder'] is not None:
        model_folder = kwargs['cellfolder']
    else:
        model_folder = info['cell_models_folder']
    params_dict['cell_models_folder'] = model_folder

    if kwargs['seed'] is not None:
        seed = kwargs['seed']
    else:
        seed = np.random.randint(1, 10000)
    params_dict['seed'] = seed

    if kwargs['folder'] is not None:
        templates_folder = kwargs['folder']
        params_dict['templates_folder'] = Path(kwargs['folder'])
    else:
        templates_folder = Path(info['templates_folder'])
    intraonly = kwargs['intraonly']

    if kwargs['rot'] is not None:
        params_dict['rot'] = kwargs['rot']
    if kwargs['n'] is not None:
        params_dict['n'] = kwargs['n']
    if kwargs['dt'] is not None:
        params_dict['dt'] = kwargs['dt']
    if kwargs['ncontacts'] is not None:
        params_dict['ncontacts'] = kwargs['ncontacts']
    if kwargs['overhang'] is not None:
        params_dict['overhang'] = kwargs['overhang']
    if kwargs['xlim'] is not None and len(kwargs['xlim']) == 2:
        params_dict['xlim'] = kwargs['xlim']
    if kwargs['ylim'] is not None and len(kwargs['ylim']) == 2:
        params_dict['ylim'] = kwargs['ylim']
    if kwargs['zlim'] is not None and len(kwargs['zlim']) == 2:
        params_dict['zlim'] = kwargs['zlim']
    if kwargs['min_amp'] is not None:
        params_dict['min_amp'] = kwargs['min_amp']

    if kwargs['drifting']:
        params_dict['drifting'] = True
    elif 'drifting' not in params_dict.keys():
        params_dict['drifting'] = False
    if kwargs['min_drift'] is not None:
        params_dict['min_drift'] = kwargs['min_drift']
    if kwargs['max_drift'] is not None:
        params_dict['max_drift'] = kwargs['max_drift']
    if kwargs['drift_steps'] is not None:
        params_dict['drift_steps'] = kwargs['drift_steps']
    if kwargs['drift_xlim'] is not None and len(kwargs['drift_xlim']) == 2:
        params_dict['drift_xlim'] = kwargs['drift_xlim']
    if kwargs['drift_ylim'] is not None and len(kwargs['drift_ylim']) == 2:
        params_dict['drift_ylim'] = kwargs['drift_ylim']
    if kwargs['drift_zlim'] is not None and len(kwargs['drift_zlim']) == 2:
        params_dict['drift_zlim'] = kwargs['drift_zlim']

    if kwargs['probe'] is not None:
        if kwargs['probe'] in mu.return_mea_list():
            params_dict['probe'] = kwargs['probe']
        else:
            print("The probe ", kwargs['probe'], " is not listead as a MEAutility probe.")
            return
    if kwargs['no_parallel']:
        parallel = False
    else:
        parallel = True
    if kwargs['njobs'] is not None:
        njobs = kwargs['njobs']
    else:
        njobs = None
    recompile = kwargs['recompile']
    verbose = kwargs['verbose']

    params_dict['templates_folder'] = str(templates_folder)

    tempgen = gt.gen_templates(cell_models_folder=model_folder,
                               params=params_dict,
                               templates_tmp_folder=str(templates_folder),
                               intraonly=intraonly,
                               n_jobs=njobs,
                               recompile=recompile,
                               parallel=parallel,
                               verbose=verbose)

    # Merge simulated data and cleanup
    if not intraonly:
        rot = params_dict['rot']
        n = params_dict['n']
        probe = params_dict['probe']
        if kwargs['fname'] is None:
            if params_dict['drifting']:
                fname = f'templates_{n}_{probe}_drift_{time.strftime("%d-%m-%Y_%H-%M")}.h5'
            else:
                fname = f'templates_{n}_{probe}_{time.strftime("%d-%m-%Y_%H-%M")}.h5'
        else:
            fname = kwargs['fname']
        save_fname = str(templates_folder / rot / fname)
        save_template_generator(tempgen, save_fname, verbose=True)


@cli.command()
@click.option('--templates', '-t', default=None,
              help='templates path')
@click.option('--params', '-prm', default=None,
              help='path to default_params.yaml (otherwise default default_params are used '
                   'and some of the parameters can be overwritten with the following options)')
@click.option('--default', is_flag=True,
              help='shows default values for simulation')
@click.option('--fname', '-fn', default=None,
              help='recording filename')
@click.option('--folder', '-fol', default=None,
              help='recording output base folder')
@click.option('--duration', '-d', default=None, type=float,
              help='duration in s (default=10)')
@click.option('--njobs', '-nj', default=None, type=int,
              help='number of jobs (default n_jobs=n_cpus)')
@click.option('--n-exc', '-ne', default=None, type=int,
              help='number of excitatory cells (default=15)')
@click.option('--n-inh', '-ni', default=None, type=int,
              help='number of inhibitory cells (default=5)')
@click.option('--f-exc', '-fe', default=None, type=float,
              help='average firing rate of excitatory cells in Hz (default=5)')
@click.option('--f-inh', '-fi', default=None, type=float,
              help='average firing rate of inhibitory cells in Hz (default=15)')
@click.option('--st-exc', '-se', default=None, type=float,
              help='firing rate standard deviation of excitatory cells in Hz (default=1)')
@click.option('--st-inh', '-si', default=None, type=float,
              help='firing rate standard deviation of inhibitory cells in Hz (default=3)')
@click.option('--min-rate', '-mr', default=None, type=float,
              help='minimum firing rate (default=0.5)')
@click.option('--ref-per', '-rp', default=None, type=float,
              help='refractory period in ms (default=2)')
@click.option('--process', '-p', default='poisson', type=click.Choice(['poisson', 'gamma']),
              help='process for generating spike trains (default=poisson)')
@click.option('--tstart', default=None, type=float,
              help='start time in s (default=0)')
@click.option('--min-dist', '-md', default=None, type=int,
              help='minumum distance between neuron in um (default=25)')
@click.option('--min-amp', '-mina', default=None, type=int,
              help='minumum eap amplitude in uV (default=50)')
@click.option('--max-amp', '-maxa', default=None, type=int,
              help='maximum eap amplitude in uV (default=inf)')
@click.option('--fs', default=None, type=float,
              help='sampling frequency in kHz (default from templates sampling frequency)')
@click.option('--sync-rate', '-sr', default=None, type=float,
              help='added synchrony rate on spatially overlapping spikes')
@click.option('--sync-jitt', '-sj', default=None, type=float,
              help='jitter in ms for added spikes')
@click.option('--noise-lev', '-nl', default=None, type=int,
              help='noise level in uV (default=10)')
@click.option('--modulation', '-m', default=None, type=click.Choice(['none', 'template', 'electrode']),
              help='modulation type')
@click.option('--chunk-duration', '-chd', default=None, type=float,
              help='chunk duration in s (default 0)')
@click.option('--st-seed', '-stseed', default=None, type=int,
              help='random seed for spike trains')
@click.option('--temp-seed', '-tseed', default=None, type=int,
              help='random seed for template selection')
@click.option('--conv-seed', '-cseed', default=None, type=int,
              help='random seed for convolution')
@click.option('--noise-seed', '-nseed', default=None, type=int,
              help='random seed for noise')
@click.option('--half-dist', '-hd', default=None, type=float,
              help='when noise is distance-correlated the distance at which covariance is 0.5 (default=30)')
@click.option('--color-noise', '-cn', is_flag=True,
              help='if True noise is colored')
@click.option('--color-peak', '-cp', default=None, type=float,
              help='peak for noise in Hz (default 500 Hz)')
@click.option('--color-q', '-cq', default=None, type=float,
              help='quality factor for noise filter (default=1)')
@click.option('--random-noise-floor', '-rnf', default=None, type=float,
              help='noise floor in std of additive noide (default 1)')
@click.option('--filter', is_flag=True,
              help='if True filter is applied')
@click.option('--filt-cutoff', '-fc', default=None, type=float, multiple=True,
              help='filter cutoff frequencies.'
                   'High-pass: -fc hp-cutoff. Band-pass: -fc hp-cutoff -fc lp-cutoff')
@click.option('--filt-order', '-fo', default=None, type=int,
              help='filter order (default 3)')
@click.option('--overlap', is_flag=True,
              help='if True it annotates overlapping spikes')
@click.option('--overlap-thresh', '-ot', type=float,
              help='overlap threshold for spatial overlap')
@click.option('--extract-wf', is_flag=True,
              help='if True it annotates overlapping spikes')
@click.option('--bursting', is_flag=True,
              help='if True ISI-dependent modulation is performed')
@click.option('--shape-mod', is_flag=True,
              help='if True shape modulation is performed')
@click.option('--drifting', '-dr', is_flag=True,
              help='generate drifting recordings')
@click.option('--preferred-dir', '-prd', default=None, nargs=3, type=float,
              help='preferred drifting direction (0 0 1 is positive z-direction)')
@click.option('--angle-tol', '-angt', type=float,
              help='angle tollerance for preferred direction')
@click.option('--drift-velocity', '-drvel', type=float,
              help='drift velocity in um/min')
@click.option('--t-start-drift', '-tsd', type=float,
              help='drifting start time in s')
@click.option('--verbose', '-v', is_flag=True,
              help='produce verbose output')
def gen_recordings(params, **kwargs):
    """Generates RECORDINGS from TEMPLATES."""
    # Retrieve default_params file
    info, config_folder = get_default_config()

    if params is None:
        with open(info['recordings_params'], 'r') as pf:
            if use_loader:
                params_dict = yaml.load(pf, Loader=yaml.FullLoader)
            else:
                params_dict = yaml.load(pf)
    else:
        with open(params, 'r') as pf:
            if use_loader:
                params_dict = yaml.load(pf, Loader=yaml.FullLoader)
            else:
                params_dict = yaml.load(pf)

    if kwargs['default'] is True:
        pprint.pprint(params_dict)
        return

    templates_folder = Path(kwargs['templates'])

    if kwargs['folder'] is not None:
        params_dict['recordings'].update({'recordings_folder': kwargs['folder']})
    else:
        params_dict['recordings'].update({'recordings_folder': info['recordings_folder']})
    recordings_folder = params_dict['recordings']['recordings_folder']

    if kwargs['templates'] is None:
        print('Provide eap templates path')
        return
    else:
        if templates_folder.is_dir() or templates_folder.suffix in ['.h5', '.hdf5']:
            params_dict['templates'].update({'templates': kwargs['templates']})
        else:
            print(kwargs['templates'])
            raise AttributeError("'templates' is not a folder")

    if kwargs['n_exc'] is not None:
        params_dict['spiketrains']['n_exc'] = kwargs['n_exc']
    if kwargs['n_inh'] is not None:
        params_dict['spiketrains']['n_inh'] = kwargs['n_inh']
    if kwargs['f_exc'] is not None:
        params_dict['spiketrains']['f_exc'] = kwargs['f_exc']
    if kwargs['f_inh'] is not None:
        params_dict['spiketrains']['f_inh'] = kwargs['f_inh']
    if kwargs['st_exc'] is not None:
        params_dict['spiketrains']['st_exc'] = kwargs['st_exc']
    if kwargs['st_inh'] is not None:
        params_dict['spiketrains']['st_inh'] = kwargs['st_inh']
    if kwargs['min_rate'] is not None:
        params_dict['spiketrains']['min_rate'] = kwargs['min_rate']
    if kwargs['ref_per'] is not None:
        params_dict['spiketrains']['ref_per'] = kwargs['ref_per']
    if kwargs['process'] is not None:
        params_dict['spiketrains']['process'] = kwargs['process']
    if kwargs['min_rate'] is not None:
        params_dict['spiketrains']['min_rate'] = kwargs['min_rate']
    if kwargs['duration'] is not None:
        params_dict['spiketrains']['duration'] = kwargs['duration']
    if kwargs['tstart'] is not None:
        params_dict['spiketrains']['t_start'] = kwargs['t_start']
    if kwargs['min_dist'] is not None:
        params_dict['templates']['min_dist'] = kwargs['min_dist']
    if kwargs['min_amp'] is not None:
        params_dict['templates']['min_amp'] = kwargs['min_amp']
    if kwargs['max_amp'] is not None:
        params_dict['templates']['max_amp'] = kwargs['max_amp']
    if kwargs['overlap_thresh'] is not None:
        params_dict['templates']['overlap_threshold'] = kwargs['overlap_thresh']

    if kwargs['noise_lev'] is not None:
        params_dict['recordings']['noise_level'] = kwargs['noise_lev']
    if kwargs['modulation'] is not None:
        params_dict['recordings']['modulation'] = kwargs['modulation']

    if kwargs['chunk_duration'] is not None:
        params_dict['recordings']['chunk_duration'] = kwargs['chunk_duration']
    if kwargs['filter']:
        params_dict['recordings']['filter'] = True
    else:
        params_dict['recordings']['filter'] = False
    if kwargs['filt_cutoff'] is not None:
        if isinstance(kwargs['filt_cutoff'], tuple):
            kwargs['filt_cutoff'] = list(kwargs['filt_cutoff'])
        params_dict['recordings']['filter_cutoff'] = kwargs['filt_cutoff']
    if kwargs['filt_order'] is not None:
        params_dict['recordings']['filt_order'] = kwargs['filt_order']
    if kwargs['fs'] is not None:
        params_dict['recordings']['fs'] = kwargs['fs']
    else:
        params_dict['recordings']['fs'] = None
    if kwargs['sync_rate'] is not None:
        params_dict['recordings']['sync_rate'] = kwargs['sync_rate']
    else:
        params_dict['recordings']['sync_rate'] = None
    if kwargs['sync_jitt'] is not None:
        params_dict['recordings']['sync_jitt'] = kwargs['sync_jitt']
    else:
        params_dict['recordings']['sync_jitt'] = 1
    if kwargs['noise_seed'] is not None:
        params_dict['seeds']['noise'] = kwargs['noise_seed']
    if kwargs['temp_seed'] is not None:
        params_dict['seeds']['templates'] = kwargs['temp_seed']
    if kwargs['st_seed'] is not None:
        params_dict['seeds']['spiketrains'] = kwargs['st_seed']
    if kwargs['conv_seed'] is not None:
        params_dict['seeds']['convolution'] = kwargs['conv_seed']
    if kwargs['overlap']:
        params_dict['recordings']['overlap'] = True
    elif 'overlap' not in params_dict['recordings'].keys():
        params_dict['recordings']['overlap'] = False
    if kwargs['extract_wf']:
        params_dict['recordings']['extract_wf'] = True
    elif 'extract_wf' not in params_dict['recordings'].keys():
        params_dict['recordings']['extract_wf'] = False

    if kwargs['half_dist'] is not None:
        params_dict['recordings']['half_dist'] = kwargs['half_dist']
    if kwargs['color_noise']:
        params_dict['recordings']['noise_color'] = True
    elif 'noise_color' not in params_dict['recordings'].keys():
        params_dict['recordings']['noise_color'] = False
    if kwargs['color_peak'] is not None:
        params_dict['recordings']['color_peak'] = kwargs['color_peak']
    if kwargs['color_q'] is not None:
        params_dict['recordings']['color_q'] = kwargs['color_q']
    if kwargs['random_noise_floor'] is not None:
        params_dict['recordings']['random_noise_floor'] = kwargs['random_noise_floor']

    if kwargs['bursting']:
        params_dict['recordings']['bursting'] = True
    elif 'bursting' not in params_dict['recordings'].keys():
        params_dict['recordings']['bursting'] = False

    if kwargs['shape_mod']:
        params_dict['recordings']['shape_mod'] = True
    elif 'shape_mod' not in params_dict['recordings'].keys():
        params_dict['recordings']['shape_mod'] = False

    if kwargs['drifting']:
        params_dict['recordings']['drifting'] = True
    elif 'drifting' not in params_dict['recordings'].keys():
        params_dict['recordings']['drifting'] = False
    if kwargs['preferred_dir'] is not None and len(kwargs['preferred_dir']) == 3:
        params_dict['recordings']['preferred_dir'] = kwargs['preferred_dir']
    if kwargs['angle_tol']:
        params_dict['recordings']['angle_tol'] = kwargs['angle_tol']
    if kwargs['drift_velocity']:
        params_dict['recordings']['drift_velocity'] = kwargs['drift_velocity']
    if kwargs['t_start_drift']:
        params_dict['recordings']['t_start_drift'] = kwargs['t_start_drift']
    if kwargs['verbose']:
        verbose = 2
    else:
        verbose = kwargs['verbose']
    if kwargs['njobs'] is not None:
        njobs = kwargs['njobs']
    else:
        njobs = None

    recgen = gt.gen_recordings(templates=kwargs['templates'], params=params_dict, verbose=verbose, n_jobs=njobs)
    info = recgen.info

    n_neurons = info['recordings']['n_neurons']
    electrode_name = info['electrodes']['electrode_name']
    duration = info['recordings']['duration']
    noise_level = info['recordings']['noise_level']

    if kwargs['fname'] is None:
        if kwargs['drifting']:
            fname = f'recordings_{n_neurons}cells_{electrode_name}_{duration}_{np.round(noise_level, 2)}uV_' \
                    f'drift_{time.strftime("%d-%m-%Y_%H-%M")}.h5'
        else:
            fname = f'recordings_{n_neurons}cells_{electrode_name}_{duration}_{np.round(noise_level, 2)}uV_' \
                    f'{time.strftime("%d-%m-%Y_%H-%M")}.h5'
    else:
        fname = kwargs['fname']

    if recordings_folder is not None:
        recordings_folder = Path(recordings_folder)
        if not recordings_folder.is_dir():
            os.makedirs(str(recordings_folder))
    rec_path = str(recordings_folder / fname)
    save_recording_generator(recgen, rec_path, verbose=True)


@cli.command()
def default_config():
    """Print default configurations."""
    info, config = get_default_config(print_version=True)
    pprint.pprint(info)


@cli.command()
@click.option('--info', is_flag=True,
              default=False,
              help='if True probe information is printed')
def available_probes(info):
    """Print available probes."""
    from pprint import pprint
    probe_list = mu.return_mea_list()
    for p in probe_list:
        probe_info = mu.return_mea_info(p)
        if 'description' not in probe_info.keys():
            probe_info['description'] = 'no description'
        if info:
            print(p)
            pprint(mu.return_mea_info(p))
        else:
            print(p, '----------', probe_info['description'])
        print()


@cli.command()
@click.argument('cell-models-folder')
def set_cell_models_folder(cell_models_folder):
    """Set default cell_models folder."""
    info, config = get_default_config()
    cell_models_folder = Path(cell_models_folder)
    if cell_models_folder.is_dir():
        info['cell_models_folder'] = str(cell_models_folder.absolute())
        with open(Path(config) / 'mearec.conf', 'w') as f:
            yaml.dump(info, f)
        print('Set default cell_models_folder to: ', cell_models_folder)
    else:
        print(cell_models_folder, ' is not a folder!')


@cli.command()
@click.argument('templates-folder')
@click.option('--create', is_flag=True, help='if True it creates the directory')
def set_templates_folder(templates_folder, create):
    """Set default templates output folder."""
    info, config = get_default_config()
    templates_folder = Path(templates_folder).absolute()
    if templates_folder.is_dir():
        info['templates_folder'] = str(templates_folder)
        with open(Path(config) / 'mearec.conf', 'w') as f:
            yaml.dump(info, f)
        print('Set default templates_folder to: ', templates_folder)
    elif create:
        os.makedirs(str(templates_folder))
        info['templates_folder'] = str(templates_folder)
        with open(Path(config) / 'mearec.conf', 'w') as f:
            yaml.dump(info, f)
        print('Set default templates_folder to: ', templates_folder)
    else:
        print(templates_folder, ' is not a folder!')


@cli.command()
@click.argument('recordings-folder')
@click.option('--create', is_flag=True, help='if True it creates the directory')
def set_recordings_folder(recordings_folder, create):
    """Set default recordings output folder."""
    info, config = get_default_config()
    recordings_folder = Path(recordings_folder).absolute()
    if recordings_folder.is_dir():
        info['recordings_folder'] = str(recordings_folder)
        with open(Path(config) / 'mearec.conf', 'w') as f:
            yaml.dump(info, f)
        print('Set default recordings_folder to: ', recordings_folder)
    elif create:
        os.makedirs(str(recordings_folder))
        info['recordings_folder'] = str(recordings_folder)
        with open(Path(config) / 'mearec.conf', 'w') as f:
            yaml.dump(info, f)
        print('Set default recordings_folder to: ', recordings_folder)
    else:
        print(recordings_folder, ' is not a folder!')


@cli.command()
@click.argument('templates-params')
def set_templates_params(templates_params):
    """Set default templates parameter file."""
    info, config = get_default_config()
    templates_params = Path(templates_params).absolute()
    if templates_params.is_file() and templates_params.suffix in ['.yaml', '.yml']:
        info['templates_params'] = str(templates_params)
        with open(Path(config) / 'mearec.conf', 'w') as f:
            yaml.dump(info, f)
        print('Set default templates_params to: ', templates_params)
    else:
        print(templates_params, ' is not a yaml!')


@cli.command()
@click.argument('recordings-params')
def set_recordings_params(recordings_params):
    """Set default recordings parameter file."""
    info, config = get_default_config()
    recordings_params = Path(recordings_params).absolute()
    if recordings_params.is_file() and recordings_params.suffix in ['.yaml', '.yml']:
        info['recording_params'] = str(recordings_params)
        with open(Path(config) / 'mearec.conf', 'w') as f:
            yaml.dump(info, f)
        print('Set default recordings_params to: ', recordings_params)
    else:
        print(recordings_params, ' is not a yaml!')
