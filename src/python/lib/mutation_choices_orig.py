import copy
import mutation_test
import numpy as np
import pandas as pd
import random
from scipy import stats
import yaml

promoter_starting_strength = 10e6
max_promoter_strength = 10e9
min_promoter_strength = 10e5
promoter_offset = 34
promoter_min_space = 35
rnase_starting_strength = 5e-3
max_rnase_strength = 1.0
min_rnase_strength = 0.0
rnase_offset = 9
rnase_min_space = 10
max_terminator_strength = 1.0
min_terminator_strength = 0.0
terminator_starting_strength = 0.3
terminator_offset = 29
terminator_min_space = 30


def add_element(genome_tracker_new, output_dir, num_genes, deg_rate, element_choice):
    """
    Proposes a muttion that adds an element on to the genome.
    """

    genome_elements = []
    spaces_dict = {}

    region_choice = 'region_{}'.format(element_choice.split('_')[1])
    #If promoter is chosen then the required amount of space to place a promoter is set
    if 'promoter' in element_choice:
        required_spaces = promoter_min_space
    #If terminator is chosen then the required amount of space to place a promoter is set
    elif 'terminator' in element_choice:
        required_spaces = terminator_min_space
    #If rnase is chosen then the required amount of space to place a promoter is set
    else:
        required_spaces = rnase_min_space
    #Appends elements that are already on the genome on to a list
    promoter = 'promoter_{}'.format(region_choice.split('_')[1])
    terminator = 'terminator_{}'.format(region_choice.split('_')[1])
    rnase = 'rnase_{}'.format(region_choice.split('_')[1])
    gene = 'gene_{}'.format(region_choice.split('_')[1])
    gene_offsetted = 'gene_{}'.format(int(region_choice.split('_')[1])+1)
    if int(region_choice.split('_')[1]) != num_genes:
        if genome_tracker_new[promoter]['start'] > 0:
            if region_choice != 'region_0':
                genome_elements.append(genome_tracker_new[promoter]['start'])
            genome_elements.append(genome_tracker_new[promoter]['stop'])
        if genome_tracker_new[rnase]['start'] > 0:
            genome_elements.append(genome_tracker_new[rnase]['start'])
            genome_elements.append(genome_tracker_new[rnase]['stop'])
        genome_elements.append(genome_tracker_new[gene_offsetted]['start'])
    if region_choice != 'region_0':
        genome_elements.append(genome_tracker_new[gene]['stop'])
        if genome_tracker_new[terminator]['start'] > 0:
            genome_elements.append(genome_tracker_new[terminator]['start'])
            if genome_tracker_new[terminator]['stop'] != genome_tracker_new['length_of_genome']:
                genome_elements.append(genome_tracker_new[terminator]['stop'])
    if int(region_choice.split('_')[1]) == num_genes and genome_tracker_new[terminator]['stop'] != genome_tracker_new['length_of_genome']:
        genome_elements.append(genome_tracker_new['length_of_genome'])
    #Determines areas within the intergenic regions that are available
    space_index = 0
    highest_position = max(genome_elements)
    while True:
        starting_position = min(genome_elements)
        genome_elements.remove(starting_position)
        ending_position = min(genome_elements)
        genome_elements.remove(ending_position)
        if ending_position - starting_position >= required_spaces:
            spaces_dict['space{}'.format(space_index)] = dict(start=starting_position, stop=ending_position)
        if ending_position == highest_position or genome_elements == []:
            break
        space_index+=1
    #Determines the position of the chosen element
    if spaces_dict != {}:
        key = random.choice(list(spaces_dict.keys()))
        starting_position = spaces_dict[key]['start']
        ending_position = spaces_dict[key]['stop']
        if 'promoter' in element_choice:
            complete = False
            #If promoter is chosen then the binding strength, and starting and endging positions are determined and the genome length is changed appropriately
            while complete == False and spaces_dict != {}:
                genome_shift = promoter_offset + 1
                if genome_tracker_new[gene_offsetted]['start'] - ending_position < promoter_offset:
                    ending_position = ending_position - (promoter_offset - (genome_tracker_new[gene_offsetted]['start'] - ending_position))
                if ending_position - starting_position >= promoter_min_space:
                    prom_start = genome_tracker_new[element_choice]['start'] = random.randint(starting_position+1, ending_position-promoter_offset)
                    prom_stop = genome_tracker_new[element_choice]['stop'] = prom_start + promoter_offset
                    genome_tracker_new[element_choice]['previous_strength'] = genome_tracker_new[element_choice]['current_strength']
                    genome_tracker_new[element_choice]['current_strength'] = promoter_starting_strength
                    genome_tracker_new = expand_genome(genome_tracker_new, num_genes, int(region_choice.split('_')[1]), genome_shift, element_choice)
                    complete = True
                else:
                    spaces_dict.pop(key)
                    if spaces_dict != {}:
                        key = random.choice(list(spaces_dict.keys()))
                        starting_position = spaces_dict[key]['start']
                        ending_position = spaces_dict[key]['stop']
        elif 'terminator' in element_choice:
            #If terminator is chosen then the binding strength, and starting and endging positions are determined and the genome length is changed appropriately
            genome_shift = terminator_offset + 1
            if ending_position - starting_position >= terminator_min_space+1 and int(region_choice.split('_')[1]) != num_genes:
                term_start = genome_tracker_new[element_choice]['start'] = random.randint(starting_position+1, ending_position-terminator_offset)
            elif ending_position - starting_position == terminator_min_space and int(region_choice.split('_')[1]) == num_genes and ending_position == genome_tracker_new['length_of_genome']:
                term_start = genome_tracker_new[element_choice]['start'] = random.randint(starting_position+1, ending_position)
            elif ending_position - starting_position >= terminator_min_space+1 and int(region_choice.split('_')[1]) == num_genes:
                term_start = genome_tracker_new[element_choice]['start'] = random.randint(starting_position+1, ending_position-terminator_offset)
            else:
                return genome_tracker_new
            term_stop = genome_tracker_new[element_choice]['stop'] = term_start + terminator_offset
            genome_tracker_new[element_choice]['previous_strength'] = genome_tracker_new[element_choice]['current_strength']
            genome_tracker_new[element_choice]['current_strength'] = terminator_starting_strength
            genome_tracker_new = expand_genome(genome_tracker_new, num_genes, int(region_choice.split('_')[1]), genome_shift, element_choice)
        else:
            #If RNase is chosen then the binding strength, and starting and endging positions are determined and the genome length is changed appropriately
            genome_shift = rnase_offset + 1
            rnase_start = genome_tracker_new[element_choice]['start'] = random.randint(starting_position+1, ending_position-rnase_offset)
            rnase_stop = genome_tracker_new[element_choice]['stop'] = rnase_start + rnase_offset
            if deg_rate:
                genome_tracker_new[element_choice]['previous_strength'] = genome_tracker_new[element_choice]['current_strength']
                genome_tracker_new[element_choice]['current_strength'] = rnase_starting_strength
            genome_tracker_new = expand_genome(genome_tracker_new, num_genes, int(region_choice.split('_')[1]), genome_shift, element_choice)
    else:
        return genome_tracker_new

    return genome_tracker_new

def remove_element(genome_tracker_new, output_dir, num_genes, deg_rate, element_choice):
    """
    Proposes a mutation that removes an element from the genome.
    """

    #Removes the selected element from the genome
    region_choice = 'region_{}'.format(element_choice.split('_')[1])
    if 'promoter' in element_choice or 'rnase' in element_choice:
        genome_shift = 10
    elif 'terminator' in element_choice:
        genome_shift = 2
    genome_tracker_new = shrink_genome(genome_tracker_new, num_genes, int(region_choice.split('_')[1]), genome_shift, element_choice)
    genome_tracker_new[element_choice]['start'] = 0
    genome_tracker_new[element_choice]['stop'] = 0
    #If modifying each individual RNase site, then the strength is set to 0
    if (deg_rate) or (deg_rate == False and 'rnase' not in element_choice):
        genome_tracker_new[element_choice]['previous_strength'] = genome_tracker_new[element_choice]['current_strength']
        genome_tracker_new[element_choice]['current_strength'] = 0

    return genome_tracker_new

def modify_element(genome_tracker_new, output_dir, num_genes, deg_rate, element_choice):
    """
    Modify an element's (that is present on the genome) strength.
    """

    #Strengths of current elements on genome are modified
    if 'promoter' in element_choice:
        genome_tracker_new[element_choice]['previous_strength'] = genome_tracker_new[element_choice]['current_strength']
        genome_tracker_new[element_choice]['current_strength'] = genome_tracker_new[element_choice]['current_strength'] * np.random.normal(1, 0.1)
        while genome_tracker_new[element_choice]['current_strength'] < min_promoter_strength or genome_tracker_new[element_choice]['current_strength'] > max_promoter_strength:
            genome_tracker_new[element_choice]['current_strength'] = genome_tracker_new[element_choice]['previous_strength'] * np.random.normal(1, 0.1)
    elif 'terminator' in element_choice:
        genome_tracker_new[element_choice]['previous_strength'] = genome_tracker_new[element_choice]['current_strength']
        genome_tracker_new[element_choice]['current_strength'] = genome_tracker_new[element_choice]['current_strength'] * np.random.normal(1, 0.1)
        while genome_tracker_new[element_choice]['current_strength'] < min_terminator_strength or genome_tracker_new[element_choice]['current_strength'] > max_terminator_strength:
            genome_tracker_new[element_choice]['current_strength'] = genome_tracker_new[element_choice]['previous_strength'] * np.random.normal(1, 0.1)
    elif 'rnase' in element_choice and deg_rate:
        genome_tracker_new[element_choice]['previous_strength'] = genome_tracker_new[element_choice]['current_strength']
        genome_tracker_new[element_choice]['current_strength'] = genome_tracker_new[element_choice]['current_strength'] * np.random.normal(1, 0.1)
        while genome_tracker_new[element_choice]['current_strength'] < min_rnase_strength or genome_tracker_new[element_choice]['current_strength'] > max_rnase_strength:
            genome_tracker_new[element_choice]['current_strength'] = genome_tracker_new[element_choice]['previous_strength'] * np.random.normal(1, 0.1)

    return genome_tracker_new

def expand_genome(genome_tracker_new, num_genes, region_choice, genome_shift, element_choice):
    """
    When an element is added, the genome length increases.
    """

    #Increases the genome size if an element is added
    for beg_point in range(region_choice, num_genes+1):

        region = 'region_{}'.format(beg_point)
        terminator = 'terminator_{}'.format(beg_point)
        promoter = 'promoter_{}'.format(beg_point)
        rnase = 'rnase_{}'.format(beg_point)
        gene_offsetted = 'gene_{}'.format(beg_point+1)

        genome_tracker_new[region]['stop']+=genome_shift
        if beg_point != region_choice and region != 'region_0':
            genome_tracker_new[region]['start']+=genome_shift
        if region != 'region_0' and beg_point != num_genes:
            if element_choice != promoter:
                if genome_tracker_new[promoter]['start'] >= genome_tracker_new[element_choice]['start'] and genome_tracker_new[promoter]['start'] > 0:
                    genome_tracker_new[promoter]['start']+=genome_shift
                    genome_tracker_new[promoter]['stop']+=genome_shift
        if region != 'region_0':
            if element_choice != terminator:
                if genome_tracker_new[terminator]['start'] >= genome_tracker_new[element_choice]['start'] and genome_tracker_new[terminator]['start'] > 0:
                    genome_tracker_new[terminator]['start']+=genome_shift
                    genome_tracker_new[terminator]['stop']+=genome_shift
        if beg_point != num_genes:
            genome_tracker_new[gene_offsetted]['start']+=genome_shift
            genome_tracker_new[gene_offsetted]['stop']+= genome_shift
            if element_choice != rnase:
                if genome_tracker_new[rnase]['start'] >= genome_tracker_new[element_choice]['start'] and genome_tracker_new[rnase]['start'] > 0:
                    genome_tracker_new[rnase]['start']+=genome_shift
                    genome_tracker_new[rnase]['stop']+=genome_shift
    genome_tracker_new['length_of_genome']+=genome_shift

    return genome_tracker_new

def shrink_genome(genome_tracker_new, num_genes, region_choice, genome_shift, element_choice):
    """
    When an element is removed, the genome length decreases.
    """

    #Decreases the genome size if an element is added
    for beg_point in range(region_choice, num_genes+1):

        region = 'region_{}'.format(beg_point)
        terminator = 'terminator_{}'.format(beg_point)
        promoter = 'promoter_{}'.format(beg_point)
        rnase = 'rnase_{}'.format(beg_point)
        gene_offsetted = 'gene_{}'.format(beg_point+1)

        genome_tracker_new[region]['stop']-=genome_shift
        if beg_point != region_choice and region != 'region_0':
            genome_tracker_new[region]['start']-=genome_shift
        if region != 'region_0' and beg_point != num_genes:
            if element_choice != promoter:
                if genome_tracker_new[promoter]['start'] >= genome_tracker_new[element_choice]['start'] and genome_tracker_new[promoter]['start'] > 0:
                    genome_tracker_new[promoter]['start']-=genome_shift
                    genome_tracker_new[promoter]['stop']-=genome_shift
        if region != 'region_0':
            if element_choice != terminator:
                if genome_tracker_new[terminator]['start'] >= genome_tracker_new[element_choice]['start'] and genome_tracker_new[terminator]['start'] > 0:
                    genome_tracker_new[terminator]['start']-=genome_shift
                    genome_tracker_new[terminator]['stop']-=genome_shift
        if beg_point != num_genes:
            genome_tracker_new[gene_offsetted]['start']-=genome_shift
            genome_tracker_new[gene_offsetted]['stop']-= genome_shift
            if element_choice != rnase:
                if genome_tracker_new[rnase]['start'] >= genome_tracker_new[element_choice]['start'] and genome_tracker_new[rnase]['start'] > 0:
                    genome_tracker_new[rnase]['start']-=genome_shift
                    genome_tracker_new[rnase]['stop']-=genome_shift
    genome_tracker_new['length_of_genome']-=genome_shift

    return genome_tracker_new

def cleanup_genome(target_file, sos_df, output_dir, num_genes, deg_rate):
    """
    Removes elements that have low strengths that are statistically insignificant to the overal gene expression pattern produced from the best found architecture.
    """

    remove_elements = []

    #Get index with lowest sum of squared error value
    sos_df = sos_df[sos_df['Accepted'] == 'yes']
    min_sos_index = sos_df[sos_df.SSE == sos_df.SSE.min()]
    min_sos_index = min_sos_index.loc[min_sos_index['Accepted'] == 'yes']['Iteration'].values[0]

    #Open genome architecture file
    with open(output_dir+'gene_{}.yml'.format(min_sos_index), 'r') as gene_elements:
        genome_tracker_best = yaml.safe_load(gene_elements)
    genome_tracker_saved = copy.deepcopy(genome_tracker_best)
    #Calculate SSE for best genome and get a range of values
    ss_best = mutation_test.test_mutation(target_file, genome_tracker_best, output_dir, 20, deg_rate, True)

    #Iterate through each element and remove them and compare SSE values of new architecture to the best architecture previously found
    for gene in range(num_genes+1):
        promoter = 'promoter_{}'.format(gene)
        terminator = 'terminator_{}'.format(gene)
        rnase = 'rnase_{}'.format(gene)
        if gene != 0:
            if genome_tracker_best[terminator]['start'] > 0:
                genome_tracker_saved[terminator]['start'] = 0
                genome_tracker_saved[terminator]['stop'] = 0
                genome_tracker_saved[terminator]['previous_strength'] = genome_tracker_saved[terminator]['current_strength']
                genome_tracker_saved[terminator]['current_strength'] = 0
                #Get SSE values range to compare to the best found architecture
                ss_comp = mutation_test.test_mutation(target_file, genome_tracker_saved, output_dir, 20, deg_rate, True)
                if stats.ttest_ind(ss_best, ss_comp)[1] >= 0.05:
                    remove_elements.append(terminator)
                #Set the genome architecture file back to original state
                genome_tracker_saved = copy.deepcopy(genome_tracker_best)
        if gene != num_genes and gene != 0:
            if genome_tracker_best[promoter]['start'] > 0:
                genome_tracker_saved[promoter]['start'] = 0
                genome_tracker_saved[promoter]['stop'] = 0
                genome_tracker_saved[promoter]['previous_strength'] = genome_tracker_saved[promoter]['current_strength']
                genome_tracker_saved[promoter]['current_strength'] = 0
                #Get SSE values range to compare to the best found architecture
                ss_comp = mutation_test.test_mutation(target_file, genome_tracker_saved, output_dir, 20, deg_rate, True)
                if stats.ttest_ind(ss_best, ss_comp)[1] >= 0.05:
                    remove_elements.append(promoter)
                #Set the genome architecture file back to original state
                genome_tracker_saved = copy.deepcopy(genome_tracker_best)
        if gene != num_genes:
            if genome_tracker_best[rnase]['start'] > 0:
                genome_tracker_saved[rnase]['start'] = 0
                genome_tracker_saved[rnase]['stop'] = 0
                if deg_rate:
                    genome_tracker_saved[rnase]['previous_strength'] = genome_tracker_saved[rnase]['current_strength']
                    genome_tracker_saved[rnase]['current_strength'] = 0
                #Get SSE values range to compare to the best found architecture
                ss_comp = mutation_test.test_mutation(target_file, genome_tracker_saved, output_dir, 20, deg_rate, True)
                if stats.ttest_ind(ss_best, ss_comp)[1] >= 0.05:
                    remove_elements.append(rnase)
                #Set the genome architecture file back to original state
                genome_tracker_saved = copy.deepcopy(genome_tracker_best)

    #Remove all elements that did not significantly alter the gene expression pattern produced
    for element in remove_elements:
        genome_tracker_saved[element]['start'] = 0
        genome_tracker_saved[element]['stop'] = 0
        if 'rnase' not in element or deg_rate:
            genome_tracker_saved[element]['previous_strength'] = genome_tracker_saved[element]['current_strength']
            genome_tracker_saved[element]['current_strength'] = 0
    ss_comp = mutation_test.test_mutation(target_file, genome_tracker_saved, output_dir, 20, deg_rate, True)
    if stats.ttest_ind(ss_best, ss_comp)[1] > 0.05:
        genome_tracker_best = copy.deepcopy(genome_tracker_saved)

    #Saves best genome architecture found
    with open(output_dir+'final/gene_best.yml', 'w') as save_yaml:
        yaml.dump(genome_tracker_best, save_yaml)
    mutation_test.test_mutation(target_file, genome_tracker_saved, output_dir, 20, deg_rate)
    save_df = pd.read_csv(output_dir+"expression_pattern.tsv", header=0, sep='\t')
    save_df.to_csv(output_dir+"final/expression_pattern_best.tsv", sep='\t', index=False)

    return