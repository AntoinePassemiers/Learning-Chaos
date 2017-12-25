# -*- coding: utf-8 -*-
# agent.py
# author : Robin Petit, Stanislas Gueniffey, Cedric Simar, Antoine Passemiers

from utils import reward_clipper
from environment import Environment
from memory import Memory
from parameters import Parameters
from dqn import DQN

import random
import numpy as np
import tensorflow as tf


class Agent:

    def __init__(self, environment):
        
        self.environment = environment
        self.memory = Memory()
        self.step = 0
        
        # initialize the DQN and target DQN (with respective placeholders)
        self.dqn_input = tf.placeholder(tf.float32, [None, Parameters.IMAGE_HEIGHT, Parameters.IMAGE_WIDTH, Parameters.M_RECENT_FRAMES], name = "DQN_input")
        self.dqn = DQN(self.dqn_input)

        self.target_dqn_input = tf.placeholder(tf.float32, [None, Parameters.IMAGE_HEIGHT, Parameters.IMAGE_WIDTH, Parameters.M_RECENT_FRAMES], name = "target_DQN_input")
        self.target_dqn = DQN(self.target_dqn_input)

        # initialize the tensorflow session and variables
        self.tf_session = tf.Session()
        self.tf_session.run(tf.global_variables_initializer())


    
    def batch_q_learning(self):
        """
        Apply Q-learning updates, or minibatch updates, to samples of experience,
        (s, a, r, s') ~ U(D), drawn at random from the pool of stored samples.
        """

        if(self.memory.get_usage() > Parameters.AGENT_HISTORY_LENGTH):
            
            state_t, action, reward, state_t_plus_1, terminal = self.memory.bring_back_memories()

            q_t_plus_1 = self.tf_session.run(self.target_dqn.q_values, {self.target_dqn_input: state_t_plus_1})
            max_q_t_plus_1 = np.max(q_t_plus_1, axis=1)

            target_q_t = (1. - terminal) * Parameters.DISCOUNT_FACTOR * max_q_t_plus_1 + reward

            _, q_t, loss = self.tf_session.run([self.dqn.optimize, self.dqn.q_values, self.dqn.error],
            {
                self.dqn.target_q = target_q_t
                self.dqn.action = action
                self.dqn_input = state_t
            })


    def observe(self, screen, action, reward, terminal):
        """
        [Article] The agent observes an image from the emulator, 
        which is a vector of pixel values representing the current screen. 
        In addition it receives a reward representing the change in game score. 

        Updates the environment's history and agent's memory and performs an SGD update
        and/or updates the Target DQN 
        """
        
        # update agent's memory and environment's history
        self.environment.add_current_screen_to_history()
        self.memory.add(screen, action, reward_clipper(reward), terminal)

        # if we started learning
        if(self.step > Parameters.REPLAY_START_SIZE):

            # Perform SGD updates at frequency [Parameters.UPDATE_FREQUENCY]
            if(not(self.step % Parameters.UPDATE_FREQUENCY)):
                self.batch_q_learning()
            
            # Update Target DQN at frequency [Parameters.TARGET_NETWORK_UPDATE_FREQUENCY]
            if(not(self.step % Parameters.TARGET_NETWORK_UPDATE_FREQUENCY)):
                self.update_target_dqn()
            


    def select_action(self):
        """
        The agent uses its experience and expertise acquired
        through deep learning to make intelligent actions (sometimes)
        """

        # compute epsilon at step t
        dt_final = Parameters.INITIAL_EXPLORATION - Parameters.FINAL_EXPLORATION
        dt = self.step - Parameters.REPLAY_START_SIZE
        eps = Parameters.FINAL_EXPLORATION + max(0., dt * (Parameters.FINAL_EXPLORATION_FRAME - max(0., dt)) / Parameters.FINAL_EXPLORATION_FRAME)

        if random.random() < eps:
            # take a random action
            action = np.random.randint(0, Parameters.ACTION_SPACE, size=1)[0]
        else:
            # take a smart action
            action = self.tf_session.run(self.dqn.smartest_action, {self.dqn_input: self.environment.get_input()})
        
        return(action)


    def update_target_dqn(self):
        """
        Update the target DQN with the value of the DQN
        This method is called at a frequency C (from Algorithm 1 in the [Article])
        """

        for learning_parameter in self.dqn.learning_parameters:
            dqn_value = self.dqn.get_value(learning_parameter)
            if(dqn_value is not None):
                self.target_dqn.set_value(learning_parameter, self.dqn.get_value(learning_parameter))
            else:
                print("Impossible to set value: None")


    def train(self):
        print("TODO tomorrow XMAS <3")
    
    def play(self):
        print("TODO tomorrow XMAS <3")

    

        