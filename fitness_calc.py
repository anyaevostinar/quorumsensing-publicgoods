#!/usr/bin/env python                                                          

import random
import numpy
import sys
import copy


WORLD_X = 100
WORLD_Y = 100
WORLD_SIZE = WORLD_X * WORLD_Y
wildtype_quorum = 0.6 #the proportion of neighbors that need to be wt for wt to produce
production_cost = -5
signal_cost = -1
reward = 4.9
coop_prob = 0.5

def findNeighbors(id):
    cellID = id
    radius = 1
    cell_x = cellID % WORLD_X
    cell_y = (cellID - cell_x)/WORLD_X
    neighbor_ids = []
    for i in range(cell_x-radius, cell_x+radius+1):
        for j in range(cell_y-radius, cell_y+radius+1):
            if i == cell_x and j == cell_y:
                continue
            if i<0:
                x = WORLD_X + i
            elif i>=WORLD_X:
                x = i-WORLD_X
            else:
                x = i

            if j<0:
                y = WORLD_Y + j
            elif j>=WORLD_Y:
                y = j-WORLD_Y
            else:
                y = j

            neighbor_ids.append(y*WORLD_X+x)

    return neighbor_ids

def calculateFitnesses(def_prop, wt_prop, uncond_prop):

    #container variables for tracking how many of each type have benefitted from a public good
    num_defector = 0
    num_wildtype = 0
    num_uncond = 0
    num_empty = 0
    num_total = 0.0
#a list for holding all the organisms
    world = []
#create random grid of the organisms
    real_def = 0.0
    real_wt = 0.0
    real_uncond = 0.0
    real_empty = 0.0

    for i in range(WORLD_SIZE):
        number = random.random()
        if number < def_prop:
            world.append("defector")
            real_def += 1
        elif (number >= def_prop) and (number < (def_prop+wt_prop)):
            world.append("wildtype")
            real_wt +=1
        elif (number >= (def_prop+wt_prop)) and (number < (def_prop+wt_prop+uncond_prop)):
            world.append("uncond")
            real_uncond += 1
        else:
            world.append("empty")
            real_empty += 1
    #print real_def/WORLD_SIZE, def_prop, real_wt/WORLD_SIZE, wt_prop, real_uncond/WORLD_SIZE, uncond_prop, real_empty/WORLD_SIZE, "empty"

#go through and figure out how many of each type will a bonus
    for org in range(len(world)):
        if world[org] == "empty":
            continue
        elif world[org] == "defector":
            continue
        elif world[org] == "uncond":
            neighbor_ids = findNeighbors(org)
            #pay cost
            num_uncond += production_cost
            for neighbor in neighbor_ids:
                if world[neighbor] == "defector":
                    num_defector += reward
                elif world[neighbor] == "uncond":
                    num_uncond += reward
                elif world[neighbor] == "wildtype":
                    num_wildtype += reward
                elif world[neighbor] == "empty":
                    num_empty += reward
        elif world[org] == "wildtype":
            #autoinducer cost
            num_wildtype += signal_cost
            neighbor_ids = findNeighbors(org)
            #first find out if wt produces
            wt_neigh_num = 0
            if random.random() < coop_prob:
                for neighbor in neighbor_ids:
                    if world[neighbor] == "wildtype":
                        wt_neigh_num += 1
                if wt_neigh_num/8.0 > wildtype_quorum:
                #pay cost
                    num_wildtype += production_cost
                #bonus to neighbors
                    for neighbor in neighbor_ids:
                        if world[neighbor] == "defector":
                            num_defector += reward
                        elif world[neighbor] == "uncond":
                            num_uncond += reward
                        elif world[neighbor] == "wildtype":
                            num_wildtype += reward
                        elif world[neighbor] == "empty":
                            num_empty += reward


    if num_defector > 0:
        relative_wt_def = float(num_wildtype)/num_defector
    else:
        relative_wt_def = 0
    return '{} {} {} {} {}'.format(num_defector, num_wildtype,  num_uncond, num_empty, relative_wt_def)


def main():
#take in proportions of each type
        
    datafile = open("fitness_calcs_def_wt.dat", 'w')
    datafile.write("treatment rep def_bonus wt_bonus uncond_bonus empty_bonus relative_wt_def def_prop wt_prop uncond_prop\n")
    
    def_props = [0.1, 0.2, 0.3,0.32,0.35,0.38, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    wt_props = [0.9, 0.8, 0.7,0.68,0.65,0.62, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]
    uncond_props = [0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0,0.0]
    assert len(def_props) == len(wt_props) and len(wt_props) == len(uncond_props), "Unequal number of proportions"



    reps = 20
    
    for p in range(len(def_props)):
        for r in range(reps):
#            print r
            fitnesses = calculateFitnesses(def_props[p], wt_props[p], uncond_props[p])
            data_line = 'def{}_wt{}_uncond{} '.format(def_props[p], wt_props[p], uncond_props[p])+str(r)+" "+fitnesses+' {} {} {}\n'.format(def_props[p], wt_props[p], uncond_props[p])
            datafile.write(data_line)
            

main()
