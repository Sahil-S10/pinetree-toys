#Common imports
import copy
import numpy as np
import pandas as pd
import random
from scipy import stats
import yaml

#promoter_min_space = 35 nucleotides
#rnase_min_space = 10 nucleotides
#terminator_min_space = 30 nucleotides

#{element: [genome_shift, starting_strengths]}
element_dict = {'promoter': [34, 10e6], 'rnase': [9, 5e-3], 'terminator': [29, 0.2]}
#{element: [min_strength, max_strength]}
element_strengths_range = {'promoter': [10e5, 10e13], 'rnase': [0.0, 1.0], 'terminator': [0.0, 1.0]}


def add_element(genome_tracker_new, output_dir, num_genes, element_choice):
    """
    Proposes a muttion that adds an element on to the genome.
    Input(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    output_dir is the path to the directory in which all the saved files are stored by the program.
    num_genes refers to the number of genes in the genome.
    element_choice is the element selected to be added.
    Output(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    """

    genome_elements = []
    index_list = []
    spaces_dict = {}

    region_choice = 'region_{}'.format(element_choice.split('_')[1])
    #Appends elements that are already on the genome on to a list
    promoter = 'promoter_{}'.format(region_choice.split('_')[1])
    terminator = 'terminator_{}'.format(region_choice.split('_')[1])
    rnase = 'rnase_{}'.format(region_choice.split('_')[1])
    gene = 'gene_{}'.format(region_choice.split('_')[1])

    #Appends base pair values in which an element can be placed between
    if int(region_choice.split('_')[1]) != num_genes:
        #If a promoter is present on the genome
        if genome_tracker_new[promoter]['start'] > 0:
            #If the region selected is not the region before the first gene
            if region_choice != 'region_0':
                genome_elements.append(genome_tracker_new[promoter]['start'])
            genome_elements.append(genome_tracker_new[promoter]['stop'])
        #If an rnase is present on the genome
        if genome_tracker_new[rnase]['start'] > 0:
            genome_elements.append(genome_tracker_new[rnase]['start'])
            genome_elements.append(genome_tracker_new[rnase]['stop'])
    #If the region selected is not the region before the first gene
    if region_choice != 'region_0':
        genome_elements.append(genome_tracker_new[region_choice]['start'])
        #If a terminator is present on the genome
        if genome_tracker_new[terminator]['start'] > 0:
            genome_elements.append(genome_tracker_new[terminator]['start'])
            #If the end of the terminator is not the end of the genome
            if genome_tracker_new[terminator]['stop'] != genome_tracker_new['length_of_genome']:
                genome_elements.append(genome_tracker_new[terminator]['stop'])
    #If the last terminator ends at the end of the genome then only append the end of the genome to avoid duplicate values
    if int(region_choice.split('_')[1]) == num_genes and genome_tracker_new[terminator]['stop'] != genome_tracker_new['length_of_genome']:
        genome_elements.append(genome_tracker_new['length_of_genome'])
    genome_elements.append(genome_tracker_new[region_choice]['stop'])

    #Determines areas within the intergenic regions that are available
    space_index = 0
    highest_position = max(genome_elements)
    while True:
        #Add positions between elements to a dictionary
        starting_position = min(genome_elements)
        genome_elements.remove(starting_position)
        ending_position = min(genome_elements)
        genome_elements.remove(ending_position)
        spaces_dict['space{}'.format(space_index)] = dict(start=starting_position, stop=ending_position)
        if ending_position == highest_position or genome_elements == []:
            break
        space_index+=1
    #Identifies the area in which to add an element in
    key = random.choice(list(spaces_dict.keys()))
    starting_position = spaces_dict[key]['start']
    ending_position = spaces_dict[key]['stop']

    #Base pair value to shift the genome by depending on the element chosen
    genome_shift = element_dict[element_choice.split('_')[0]][0] + 1
    if starting_position + 1 == ending_position:
        ending_position+=1
    #Adds the element to the genome with its starting strength
    start = genome_tracker_new[element_choice]['start'] = np.random.randint(starting_position+1, ending_position)
    stop = genome_tracker_new[element_choice]['stop'] = start + element_dict[element_choice.split('_')[0]][0]
    genome_tracker_new[element_choice]['previous_strength'] = genome_tracker_new[element_choice]['current_strength']
    genome_tracker_new[element_choice]['current_strength'] = element_dict[element_choice.split('_')[0]][1]
    #Increase the length of the genome by the genome_shift value
    genome_tracker_new = expand_genome(genome_tracker_new, genome_shift, element_choice)

    return genome_tracker_new

def remove_element(genome_tracker_new, output_dir, num_genes, element_choice):
    """
    Proposes a mutation that removes an element from the genome.
    Input(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    output_dir is the path to the directory in which all the saved files are stored by the program.
    num_genes refers to the number of genes in the genome.
    element_choice is the element selected to be removed.
    Output(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    """

    #Decrease the length of the genome by the genome_shift value
    genome_tracker_new = shrink_genome(genome_tracker_new, element_dict[element_choice.split('_')[0]][0]+1, element_choice)
    #Removes the selected element from the genome
    genome_tracker_new[element_choice]['start'] = 0
    genome_tracker_new[element_choice]['stop'] = 0
    genome_tracker_new[element_choice]['previous_strength'] = genome_tracker_new[element_choice]['current_strength']
    genome_tracker_new[element_choice]['current_strength'] = 0

    return genome_tracker_new

def modify_element(genome_tracker_new, output_dir, element_choice):
    """
    Modify an element's (that is present on the genome) strength.
    Input(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    output_dir is the path to the directory in which all the saved files are stored by the program.
    element_choice is the element selected to be modified.
    Output(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    """

    #Modify the strength of the selected element present on the genome
    genome_tracker_new[element_choice]['previous_strength'] = genome_tracker_new[element_choice]['current_strength']
    genome_tracker_new[element_choice]['current_strength'] = genome_tracker_new[element_choice]['current_strength'] * np.random.normal(1, 0.1)
    #If the modified strength goes below the minimum threshold or above the maximum threshold, continue to modify the element's strength
    while genome_tracker_new[element_choice]['current_strength'] < element_strengths_range[element_choice.split('_')[0]][0] or genome_tracker_new[element_choice]['current_strength'] > element_strengths_range[element_choice.split('_')[0]][1]:
        genome_tracker_new[element_choice]['current_strength'] = genome_tracker_new[element_choice]['previous_strength'] * np.random.normal(1, 0.1)

    return genome_tracker_new

def swap_genes(genome_tracker_new, output_dir, gene_choices):
    """
    Swap the positions of two genes and modify the length of the genome.
    Input(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    output_dir is the path to the directory in which all the saved files are stored by the program.
    gene_choices is a list containing the genes selected to be modified.
    Output(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    """

    #Get lengths of genes
    first_gene_diff = genome_tracker_new[gene_choices[0]]['stop'] - genome_tracker_new[gene_choices[0]]['start']
    second_gene_diff = genome_tracker_new[gene_choices[1]]['stop'] - genome_tracker_new[gene_choices[1]]['start']

    #Saves the start and stop locations of the first gene in the list
    tmp_start = genome_tracker_new[gene_choices[0]]['start']

    #Assigns the start and stop positions of the second gene to the first
    genome_tracker_new[gene_choices[0]]['start'] = genome_tracker_new[gene_choices[1]]['start']
    genome_tracker_new[gene_choices[0]]['stop'] = genome_tracker_new[gene_choices[0]]['start'] + first_gene_diff

    #Assigns the start and stop positions of the first gene to the second
    genome_tracker_new[gene_choices[1]]['start'] = tmp_start
    genome_tracker_new[gene_choices[1]]['stop'] = tmp_start + second_gene_diff


    #If gene lengths are not equal
    if first_gene_diff != second_gene_diff:
        #Base pairs to add or remove from genome
        genome_shift = max(first_gene_diff, second_gene_diff) - min(first_gene_diff, second_gene_diff)

        #Assign longer and shorter genes
        if first_gene_diff < second_gene_diff:
            short_gene = gene_choices[0]
            long_gene = gene_choices[1]
        else:
            long_gene = gene_choices[0]
            short_gene = gene_choices[1]

        #Modify genome length based on gene lengths
        if genome_tracker_new[long_gene]['start'] > genome_tracker_new[short_gene]['stop']:
            genome_tracker_new = expand_genome(genome_tracker_new, genome_shift, long_gene)
            genome_tracker_new = shrink_genome(genome_tracker_new, genome_shift, short_gene)
        else:
            genome_tracker_new = shrink_genome(genome_tracker_new, genome_shift, short_gene)
            genome_tracker_new = expand_genome(genome_tracker_new, genome_shift, long_gene)

    return genome_tracker_new

def expand_genome(genome_tracker_new, genome_shift, element_choice):
    """
    When an element is added, the genome length increases.
    Input(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    num_genes refers to the number of genes in the genome.
    region_choice is the region the selected element resides in.
    genome_shift is the amount of base pairs to add to the genome when an element is added in.
    element_choice is the element selected to be added.
    Output(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    """

    #Increases the genome size if an element is added
    for key in genome_tracker_new:
        if key != "length_of_genome" and key != "num_genes":
            if genome_tracker_new[key]['stop'] >= genome_tracker_new[element_choice]['start']:
                #Don't add bases to start of intragenic region containing new element unless the element is a gene
                if "region_{}".format(element_choice.split("_")[1]) != key or "gene" in element_choice:
                    genome_tracker_new[key]['start']+=genome_shift
                genome_tracker_new[key]['stop']+=genome_shift
        elif key == "length_of_genome":
            genome_tracker_new["length_of_genome"]+=genome_shift

    return genome_tracker_new

def shrink_genome(genome_tracker_new, genome_shift, element_choice):
    """
    When an element is removed, the genome length decreases.
    Input(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    num_genes refers to the number of genes in the genome.
    region_choice is the region the selected element resides in.
    genome_shift is the amount of base pairs to remove from the genome when an element is removed.
    element_choice is the element selected to be removed.
    Output(s):
    genome_tracker_new is the dataframe containing the most recently edited genomic data.
    """

    #Decreases the genome size if an element is added
    for key in genome_tracker_new:
        if key != "length_of_genome" and key != "num_genes":
            if genome_tracker_new[key]['stop'] >= genome_tracker_new[element_choice]['start']:
                #Don't remove bases to start of intragenic region containing new element unless the element is a gene
                if "region_{}".format(element_choice.split("_")[1]) != key or "gene" in element_choice:
                    genome_tracker_new[key]['start']-=genome_shift
                genome_tracker_new[key]['stop']-=genome_shift
        elif key == "length_of_genome":
            genome_tracker_new["length_of_genome"]-=genome_shift

    return genome_tracker_new
