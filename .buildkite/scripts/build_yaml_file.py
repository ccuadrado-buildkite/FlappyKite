import yaml
import subprocess

BUILD_TARGETS = {} 
MAX_STEPS = 2500

steps_dict = { 
    "steps" : []
}
subprocess.run(["mkdir","-p","tmp"])

with open("tmp/output.txt", "w",encoding="UTF-8") as f:
    subprocess.run(["bazel",
                "query",
                'deps(//FlappyKite:FlappyKite)',
                "--notool_deps", 
                "--output", "minrank"],
                check=True,
                stdout=f)
f.close()

def parse_line(line):
    key,target = line.split(" ",1)
    if int(key) in BUILD_TARGETS:
        print(repr(target.rstrip()))
        BUILD_TARGETS[int(key)].append(target.rstrip())
        return
    BUILD_TARGETS[int(key)] = [target]
    
with open('tmp/output.txt') as fp:
    for line in fp:
        parse_line(line)
    fp.close()

def bazel_build_command(target):
    return {"command": f"bazel --bazelrc=.bazelrc build '%s'" % (target),
            "label": "%s" % target}

def build_step_yaml():
    step = 0
    starting_key = max(BUILD_TARGETS.keys())
    while starting_key >= 0:
        for target in BUILD_TARGETS[starting_key]:
            print(f"Adding {target.rstrip()} to build steps")
            if step <= MAX_STEPS:
                if target.startswith("//"):
                    steps_dict["steps"].append(bazel_build_command(target.rstrip()))
                    step += 1
            else:
                print(f"Max Step Count Reached, at level {starting_key} Aborting...")
                break
        starting_key -= 1
        if len(steps_dict["steps"]) > 1 and (steps_dict["steps"][-1] != {"wait":"Waiting for all nodes at depth to complete"} or steps_dict["steps"][-1] != None):
            steps_dict["steps"].append({"wait":"Waiting for all nodes at depth to complete"})
        
   
    with open('tmp/pipeline_steps.yml', 'w') as outfile:
        yaml.safe_dump(steps_dict, outfile,default_flow_style=False,sort_keys=False,default_style='')
    outfile.close()
    
build_step_yaml()