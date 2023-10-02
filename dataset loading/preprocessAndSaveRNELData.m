% Creates and saves Matlab struct of relevant data for export to python
    clear; clc;

%% Choose name for output
    dataset = 'CRS02b_1998_set1';
    saveDir = ['D:\RNEL Data\',dataset];
    saveData = true; 
    
%% Load data
    datafolder = 'D:\RNEL Data\';
    [~, idata, files, pathname] = prepData();

%% Preallocate data struct
    %Set up sub-structs
    rawSpikes = struct('timestamp',[],'channel',[],'waveform',[]);
    binnedSpikes = struct('binTimes',[],'binCounts',[]);
    stimInfo = struct('pulseTimes',[],'trainStartTimes',[],'channel',[],'frequency',[],'amplitude',[]);
    notes = struct('instructedNotes',[],'classifiedNotes',[]);
    %Combine into data struct
    data = struct('rawSpikes',rawSpikes,'binnedSpikes',binnedSpikes,'stimInfo',stimInfo,'notes',notes);
    
%% Extract rawSpikes
    % channel of recorded spike from NSP1:
    data.rawSpikes.channel = idata.QL.Data.SPIKE_SNIPPET.ss.channel(idata.QL.Data.SPIKE_SNIPPET.ss.source_index == 0);
    % timestamps of recorded spike from NSP1:
    data.rawSpikes.timestamp = idata.QL.Data.SPIKE_SNIPPET.ss.source_timestamp(idata.QL.Data.SPIKE_SNIPPET.ss.source_index == 0);
    % spike waveform:
    data.rawSpikes.waveform = idata.QL.Data.SPIKE_SNIPPET.ss.snippet(:,idata.QL.Data.SPIKE_SNIPPET.ss.source_index == 0) ;
    
%% Extract binnedSpikes
    % times for bins
    data.binnedSpikes.binTimes = idata.QL.Data.SPM_SPIKECOUNT.source_timestamp(1,:);
    % bin counts
    data.binnedSpikes.binCounts = idata.QL.Data.SPM_SPIKECOUNT.counts;
    
%% Extract stimInfo
    %extract STIM_SYNC_EVENT timing of NSP1
    idx_NSP1 = find(idata.QL.Data.STIM_SYNC_EVENT.source_index == 0); % 0 = NSP1, 1 = NSP2
    timestamps_NSP1 = idata.QL.Data.STIM_SYNC_EVENT.source_timestamp(idx_NSP1);   
    %get start of stim pulse only (there are two STIM_SYNC_EVENTS per stim pulse)
    pulse_type_NSP1 = idata.QL.Data.STIM_SYNC_EVENT.data(idx_NSP1);
    all_pulse_types = unique(pulse_type_NSP1);
    idx_pulse1 = find(pulse_type_NSP1 == all_pulse_types(1));
    pulse_times1 = timestamps_NSP1(idx_pulse1);
    %extract start times of each stim train NSP1
    diff_pulses = diff(pulse_times1); % difference between individual spikes:
    start_pulse_trains = (diff_pulses > 0.5); % next trains, there is about 1s between each stim train
    start_pulse_trains = [1 start_pulse_trains]; % add first pulse which also adjusts the vector to the correct position
    train_start_idx = find(start_pulse_trains>0);
    diff_starts = diff(train_start_idx); % each stim train should be 50 samples
    train_start_times1 = pulse_times1(train_start_idx+1); % extract actual start times
    % extract stim_channels
    stim_channels = idata.QL.Data.CERESTIM_CONFIG_CHAN_PRESAFETY.channel(1,:);
    
    %pulse times
    data.stimInfo.pulseTimes = pulse_times1;
    %train start times
    data.stimInfo.trainStartTimes = train_start_times1;
    %stimulation channel
    data.stimInfo.channel = stim_channels(train_start_idx+1);
    %stim frequency
    data.stimInfo.frequency = [diff_starts (numel(pulse_times1)-train_start_idx(end))+1];
    %stim amplitude 
    data.stimInfo.amplitude = idata.QL.Data.CERESTIM_CONFIG_MODULE.amp1(1,:);
    
%% Extract notes
    mid_active_assist = 50; % instructed notes coming from the game
    mid_spike_extraction = 30; % predicted notes coming from the classifier
    game_notes_idx = find(idata.QL.Data.CONTROL_SPACE_COMMAND.src == mid_active_assist);
    classifier_notes_idx = find(idata.QL.Data.CONTROL_SPACE_COMMAND.src == mid_spike_extraction);

    %instructed notes
    data.notes.instructedNotes = idata.QL.Data.CONTROL_SPACE_COMMAND.command(:,game_notes_idx);
    %classifier notes
    data.notes.classifiedNotes = idata.QL.Data.CONTROL_SPACE_COMMAND.command(:,classifier_notes_idx);
    
%% Save 
    if saveData
        save(fullfile(saveDir,[dataset,'.mat']),'data');
    end