#fdougher
#!/usr/bin/env python3
import sys
import csv
from collections import deque


# Read NTM description from a CSV file
def read_ntm_file(filename):
    machine_info = {}
    transitions = {} 
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

            machine_info['name'] = lines[0].strip()  # Machine name (line 1)
            machine_info['states'] = lines[1].strip().split(',')  # States (line 2)
            machine_info['input_symbols'] = lines[2].strip().split(',')  # Input symbols (line 3)
            machine_info['tape_symbols'] = lines[3].strip().split(',')  # Tape symbols (line 4)
            machine_info['start_state'] = lines[4].strip()  # Start state (line 5)
            machine_info['accept_state'] = lines[5].strip()  # Accept state (line 6)
            machine_info['reject_state'] = lines[6].strip()
            
            for line in lines[7:]: #gerenate rules
                current_state, input_symbol, next_state, write_symbol, direction = line.strip().split(',')

                key = (current_state, input_symbol) #for nondeterminism, we create a dict of possible transiotns given any state and input
                transition = (next_state, write_symbol, direction)
                if key in transitions:
                    transitions[key].append(transition)
                else:
                    transitions[key] = [transition]
    except:
        print(f"Invalid Filename, Exiting Program")
        sys.exit(1)
    #print(transitions)
    return machine_info, transitions

# Run the NTM simulation
def run_ntm(filename, input_string, max_depth=1000, max_steps=10000):
    machine_info,transitions = read_ntm_file(filename)

    tape = list(input_string) + ['_']  # append ['_']
    initial_config = (tuple(tape), machine_info['start_state'], 0) #(tape_content, state, head_position)
    
    # BFS variables
    configs_at_depth = [[initial_config]]  #starting configuration
    visited_configs = set()  # To avoid re-processing the same configuration
    visited_configs.add(initial_config)
    steps = 0
    total_transitions = 0

    print(f"Machine: {machine_info['name']}")
    print(f"Input string: {input_string}")
    calculate_average_value_count(transitions) #calc avg nondeterminism

    for depth in range(max_depth):
        next_level = []
        for config in configs_at_depth[depth]:
            tape, state, head = config
            steps+=1
            if state == machine_info['accept_state']:
                print(f"Depth of tree: {depth}")
                print(f"Total transitions: {total_transitions}")
                print(f"String accepted in {total_transitions} transitions.")
                print_path(configs_at_depth, depth)
                return
            if state == machine_info['reject_state']:
                continue 
            # Get possible transitions
            if (state, tape[head]) in transitions:
                for next_state, new_tape_char, direction in transitions[(state, tape[head])]:
                    new_tape = list(tape)
                    new_tape[head] = new_tape_char
                    new_head = head + 1 if direction == 'R' else head - 1

                    '''
                    # Handle out-of-bounds tape (when head moves beyond the current tape)
                    if new_head < 0:
                        new_tape.insert(0, '_')  # Add blank at the left end
                        new_head = 0
                    elif new_head >= len(new_tape):
                        new_tape.append('_')  # Add blank at the right end
                    '''

                    next_config = (tuple(new_tape), next_state, new_head)
                    if next_config not in visited_configs:
                        visited_configs.add(next_config)
                        next_level.append(next_config)
                    total_transitions += 1
    
        if not next_level:  #no more  configurations, reject
            print(f"Depth of tree: {depth}")
            print(f"Total transitions: {total_transitions}")  
            print(f"String rejected in {total_transitions} transitions.")
            return

        configs_at_depth.append(next_level)
        #steps += len(next_level)

        if steps > max_steps:
            print(f"Depth of tree: {depth}")
            print(f"Total transitions: {total_transitions}")
            print(f"Execution stopped after {steps} steps.")
            return
    
    print(f"Depth of tree: {depth}")
    print(f"Total transitions: {total_transitions}")
    print(f"Execution exceeded maximum depth of {max_depth}.")

def print_path(configs_at_depth, depth): #print the path of the TM
    for level in range(depth + 1):
        for config in configs_at_depth[level]:
            tape, state, head = config
            left_of_head = ''.join(tape[:head])  # Left of the head
            head_char = tape[head] if head < len(tape) else '_'
            right_of_head = ''.join(tape[head + 1:])  # Right of the head

            print(f"{left_of_head} {state} {head_char} {right_of_head}")

#average nondeterminism - average number of values with keys
def calculate_average_value_count(input_dict):
    total_values = 0
    total_keys = len(input_dict)
    for key, values in input_dict.items():
        total_values += len(values)
    if total_keys > 0:
        average = total_values / total_keys
        print(f"Average Nondeterminism: {average}")
    else: 
        print("No keys to calculate")


def main(arguments=sys.argv[1:])->None:
    filename = ""
    input_string = ""
    max_depth = 0
    max_steps = 0
    
    #parse command line arguments
    if arguments:
        filename = arguments.pop(0)
    if arguments:
        input_string = arguments.pop(0)
    if arguments:
        max_depth = int(arguments.pop(0))
    if arguments:
        max_steps = int(arguments.pop(0))
    if arguments:
        print("Too many arguments passed, excess will be ignored")

    #for each possible input, if they are empty ask for user input
    if not arguments:
        if not filename:
            filename = input(f"Machine file: ")
        if not input_string:
            input_string = input(f"Input String: ")
        
        if max_depth == 0:
            try:
                max_depth = int(input(f"Max Depth: "))
            except ValueError:
                max_depth = 1000
                print("Invalid input, Using 1000 as default")
        if max_steps == 0:
            try:
                max_steps = int(input(f"Max Steps: "))
            except ValueError:
                max_steps = 10000
                print("Invalid input, Using 10000 as default")


    #process NTM
    print(f"\nRunning the {filename} Turing Machine with input '{input_string}' and max depth of {max_depth} and max steps of {max_steps}\n")
    run_ntm(filename,input_string,max_depth,max_steps)


if __name__=='__main__':
    main()
    #filename = "equal01.csv"
    #input_string = "aa"
    #run_ntm(filename,input_string)
