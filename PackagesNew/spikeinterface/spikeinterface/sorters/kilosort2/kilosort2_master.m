try
    fprintf('Beginning kilosort2_master.m execution \n')
    % prepare for kilosort execution
    addpath(genpath('{kilosort2_path}'));
    
    fprintf('Step 1 \n')
    % set file path
    fpath = '{output_folder}';
    
    fprintf('Step 1.1 \n')
    % add npy-matlab functions (copied in the output folder)
    addpath(genpath(fpath));

    fprintf('Step 1.2 \n')
    % create channel map file
    run(fullfile('{channel_path}'));

    fprintf('Step 2 \n')
    % Run the configuration file, it builds the structure of options (ops)
    run(fullfile('{config_path}'))

    ops.trange = [0 Inf]; % time range to sort

    fprintf('Step 3 \n')
    % preprocess data to create temp_wh.dat
    rez = preprocessDataSub(ops);

    fprintf('kilosort2_master.m finished preprocessDataSub function')
    % time-reordering as a function of drift
    rez = clusterSingleBatches(rez);

    % main tracking and template matching algorithm
    rez = learnAndSolve8b(rez);

    % final merges
    rez = find_merges(rez, 1);

    % final splits by SVD
    rez = splitAllClusters(rez, 1);

    % final splits by amplitudes
    rez = splitAllClusters(rez, 0);

    % decide on cutoff
    rez = set_cutoff(rez);

    fprintf('found %d good units \n', sum(rez.good>0))

    fprintf('Saving results to Phy  \n')
    rezToPhy(rez, fullfile(fpath));
catch
    fprintf('----------------------------------------');
    fprintf(lasterr());
    quit(1);
end
quit(0);
