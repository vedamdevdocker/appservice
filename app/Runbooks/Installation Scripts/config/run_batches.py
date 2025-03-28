import os
import subprocess

def get_sorted_batch_files(directory, num_prefix_chars):
    """Retrieve and sort batch files based on the numeric prefix."""
    batch_files = []
    
    for file in os.listdir(directory):
        if file.endswith(".bat") and file[:num_prefix_chars].isdigit():
            batch_files.append((int(file[:num_prefix_chars]), os.path.join(directory, file)))
    
    return [file[1] for file in sorted(batch_files, key=lambda x: x[0])]

def execute_batch_files(batch_files):
    """Execute a list of batch files sequentially."""
    for batch_file in batch_files:
        batch_dir = os.path.dirname(batch_file)  # Get the directory of the batch file
        os.chdir(batch_dir)  # Change the working directory
        print(f"Executing: {batch_file} in {batch_dir}")
        subprocess.run(batch_file, shell=True)

if __name__ == "__main__":
    current_directory = os.getcwd()
    instance_directory = os.path.join(current_directory, "instance")

    # Execute batch files in "instance" folder (sorted by first 3 characters)
    if os.path.exists(instance_directory):
        instance_batches = get_sorted_batch_files(instance_directory, 3)
        execute_batch_files(instance_batches)
    else:
        print(f"Directory not found: {instance_directory}")

    # Execute batch files in the current directory (sorted by first 2 characters)
    main_batches = get_sorted_batch_files(current_directory, 2)
    execute_batch_files(main_batches)

    print("All batch files processed successfully.")
