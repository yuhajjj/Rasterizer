def format_obj(filename):

    #open file and write to string txt
    with open(filename, "r") as file:
        txt = file.read()

    lines = txt.split("\n")

    #may need to implement strip here

    #initialized all lists, only returns vertex and face bc for now we are only working with those
    vertex_array = []
    normal_array =[]
    texture_array = []
    facesiv_array = []

    #loops through lines and creates a list for each data type
    for line in lines:
        if line.startswith("v "):
            formatted = line[1:].split()
            vertex_array.append([int(float(a)) for a in formatted])    #integers, but may need to convert to float in the future
        
        elif line.startswith("f "):
            formatted = line[1:].split()
            facesiv_array.append([int(float(a[0])) - 1 for a in formatted])

            
    return(vertex_array, facesiv_array)


