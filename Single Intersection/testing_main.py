from __future__ import absolute_import
from __future__ import print_function

import os
from shutil import copyfile

from testing_simulation import Simulation
from generator import TrafficGenerator
from model import TestModel
from visualization import Visualization
from utils import import_test_configuration, set_sumo, set_test_path


if __name__ == "__main__":

    config = import_test_configuration(config_file='testing_settings.ini')
    sumo_cmd = set_sumo(config['gui'], config['sumocfg_file_name'], config['max_steps'])
    model_path, plot_path = set_test_path(config['models_path_name'], config['model_to_test'])

    Model = TestModel(
        input_dim=config['num_states'],
        model_path=model_path
    )

    TrafficGen = TrafficGenerator(
        config['max_steps'], 
        config['n_cars_generated'],
        config['percentage_CV']
    )

    Visualization = Visualization(
        plot_path, 
        dpi=96
    )
        
    Simulation = Simulation(
        Model,
        TrafficGen,
        sumo_cmd,
        config['max_steps'],
        config['green_duration'],
        config['yellow_duration'],
        config['num_states'],
        config['num_actions']
    )

    #Baseline Round Robin Performance
    print('\n----- Test episode - Traditional(Round Robin) lights -----')
    simulation_time = Simulation.run(config['episode_seed'],light_controls='round_robin')  # run the simulation
    print(f"Average Queue length : {sum(Simulation.queue_length_episode) / len(Simulation.queue_length_episode)}        Cumulative Reward obtained : {sum(Simulation.reward_episode)}            Cumulative Wait time : {Simulation.cumulative_wait_times[-1]}")
    print('Simulation time:', simulation_time, 's')

    rr_reward_episode = Simulation.reward_episode
    rr_queue_length_episode = Simulation.queue_length_episode
    rr_cumulative_wait_times = Simulation.cumulative_wait_times

    
    #Agent Performance
    print('\n----- Test episode - Agent controlled lights -------')
    simulation_time = Simulation.run(config['episode_seed'],light_controls='agent')
    print(
        f"Average Queue length : {sum(Simulation.queue_length_episode) / len(Simulation.queue_length_episode)}        Cumulative Reward obtained : {sum(Simulation.reward_episode)}            Cumulative Wait time : {Simulation.cumulative_wait_times[-1]}")
    print('Simulation time:', simulation_time, 's')

    agent_reward_episode = Simulation.reward_episode
    agent_queue_length_episode = Simulation.queue_length_episode
    agent_cumulative_wait_times = Simulation.cumulative_wait_times


    print("----- Testing info saved at:", plot_path)

    copyfile(src='testing_settings.ini', dst=os.path.join(plot_path, 'testing_settings.ini'))

    Visualization.save_data_and_plot(data=Simulation.reward_episode, filename='reward', xlabel='Action step', ylabel='Reward',title='Penetration rate = '+str(config['percentage_CV'])+'%')
    Visualization.save_data_and_plot(data=Simulation.queue_length_episode, filename='queue', xlabel='Step', ylabel='Queue lenght (vehicles)',title='Penetration rate = '+str(config['percentage_CV'])+'%')
    Visualization.save_data_and_plot(data=Simulation.cumulative_wait_times, filename='queue', xlabel='Step', ylabel='Queue lenght (vehicles)',title='Penetration rate = '+str(config['percentage_CV'])+'%')
    legend = ['Agent', 'Round Robin']
    Visualization.save_data_and_plot(data=[agent_reward_episode, rr_reward_episode],
                               filename='reward', xlabel='Action step',
                               ylabel='Reward', title='Penetration rate = '+str(config['percentage_CV'])+'%',legend=legend)
    Visualization.save_data_and_plot(
        data=[agent_queue_length_episode, rr_queue_length_episode],
        filename='queue', xlabel='Step',
        ylabel='Queue length (vehicles)', title='Penetration rate = '+str(config['percentage_CV'])+'%',legend=legend)
    Visualization.save_data_and_plot(data=
                               [agent_cumulative_wait_times, rr_cumulative_wait_times,
                                ],
                               filename='wait_time', xlabel='Step',
                               ylabel='Cumulative wait time',title='Penetration rate = '+str(config['percentage_CV'])+'%', legend=legend)