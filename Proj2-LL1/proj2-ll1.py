rules: dict[str, list[str]] = dict()
follow_dict: dict[str, list[str]] = dict()
start: str = ""
epsilon: str = "ε"

# vom folosi neterminal = uppercase, terminal = lowercase

# Prima linie va fi simbolul de start
with open("cfg.txt") as f:
    start = f.readline()[:-1]
    print("start -", start)

    # fiecare neterminal este definit pe 1 linie
    # structura este X->orice|orice2|orice3...
    while line := f.readline():
        rules[line[0]] = line[3:-1].split('|')

#### Logica pentru first si follow:
# https://www.geeksforgeeks.org/compiler-design/why-first-and-follow-in-compiler-design/

def first(c : str) -> list[str]:
    if c.islower(): return c # daca este terminal il returnam direct

    res = []

    # cautam primul element terminal, daca gasit neterminal X atunci adaugam first(X)
    for prod in rules[c]:
        for i in prod:
            if i == c: continue

            if i.islower():
                res.append( i )

            if i.isupper():
                res.extend( first(i) )
    
    return list(set(res))

def get_first_dict():
    return {key : first(key) for key in rules}

# folosit in follow, daca simbolul exista deja atunci nu il adaugam
def add_unique_to_dict(d : dict[str, list[str]], key : str, char : str) -> bool:
    if char == epsilon: return False
    if char in d[key]: return False
    else:
        d[key].append(char)
        return True

def get_follow_dict():
    # initializam dictionar gol cu fiecare simbol neterminal
    follow_dict = {key : [] for key in rules}
    follow_dict[start].append("$")

    # Cand nu se mai updateaza nici unul oprim loop-ul
    changed = True
    while changed:
        changed = False # facem update la True daca a fost adaugat ceva folosind functia add_unique_to_dict

        # Iteram prin fiecare netermial
        for key in rules:

            # Cautam neterminalul in toate expresiile ceilorlalty neterminali
            for key2 in rules:
                #print("checking ", key, " in ", key2)

                for prop in rules[key2]:
                    #print("checking ", prop)
                    if key in prop:
                        key_idx = prop.index(key)
                        #print(key_idx)

                        # Daca este ultimul din enunt atunci updatam cu neterminalul car are aceasta expresie
                        # ex: follow(B) ---- A -> cB atunci adaugam FOLLOW(A) 
                        if key_idx == len(prop) - 1:
                            # Deoarece ne folosim de follow(key2) evitam loop infinit
                            if key == key2: continue

                            # trecem prin follow() a neterminalului key2 suntem si adaugam la key 
                            for char in follow_dict[key2]:
                                if add_unique_to_dict(follow_dict, key, char):
                                    changed = True
                        
                        # Daca key se la inceput/mijlocul expresiei atunci adaugam FIRST() din urmatorul element (ne?)terminal
                        # Presupune ca first_dict a fost calculat deja!
                        else:
                            for char in first(prop[key_idx + 1]):
                                #print(f"{key} in {key2} in prop {prop} with {char}")
                                if add_unique_to_dict(follow_dict, key, char):
                                    changed = True
        
        #changed = False
    
    return follow_dict


def generate_recursive_descent_parser(input : str):

    def add_libs(f):
        f.write("#include <iostream>\n")
        f.write("#include <string>\n\n")
    
    # next = caracterul care urmeaza sa fie citit
    # idx = indexul acestuia
    def add_globals(f):
        f.write(f"std::string input = \"{input}\";\n")
        f.write("std::string output = \"\";\n")
        f.write("char next = input[0];\n")
        f.write("int idx = 0;\n\n")
    
    # citeste un caracter si daca este corect trece la urmatorul
    def add_helper_reader(f):
        f.write("bool read(char c) {\n")
        f.write("   if( c == next ) {\n")
        f.write(f"   std::cout<<\"reading char \"<<c<<\"\\n\";\n")
        f.write("      idx++;\n")
        f.write("      next = input[idx];\n")
        f.write("      return true;\n")
        f.write("   }\n")
        f.write("   return false;\n")
        f.write("};\n\n")
    
    def add_function_definitions(f):
        for i in rules:
            f.write(f"bool {i}(); ")
        f.write('\n\n')

    def add_parse_function(f, name):
        f.write(f"bool {name}() {{\n")
        f.write(f"   output += \"{name}\";\n")
        f.write(f"   std::cout<<\"{name}\"<<\"-\"<<\"char:\"<<next<<\"-\"<<\"idx:\"<<idx<<\"\\n\";\n")

        nullable = False
        # trece prin fiecare regula a neterminalului
        for prop_idx, prop in enumerate(rules[name]):
            # pentru fiecare element al expresiei se genereaza un if
            # daca poate fi epsilon, inlocuim return false cu return true la sfarsit
            for i in range( len(prop) ):
                if prop == epsilon:
                    nullable = True
                    continue

                if i == 0:
                    # daca este terminal verificam daca terminalul este egal cu caracterul urmat la citit
                    if prop[i].islower():
                        if prop_idx == 0: # Adaugam IF ELSE daca nu este prima expresie
                            f.write(f"   if( next == '{prop[i]}' ) {{\n")
                        else:
                            f.write(f"   else if( next == '{prop[i]}' ) {{\n")
                    
                    # daca este neterminal verificam daca caracterul de citit se afla in first()
                    if prop[i].isupper():
                        first_set = [x for x in first(prop[i]) if x != epsilon]
                        if prop_idx == 0:
                            f.write(f"   if( std::string(\"{''.join(first_set)}\").find(next) != std::string::npos ) {{\n")
                        else:
                            f.write(f"   else if( std::string(\"{''.join(first_set)}\").find(next) != std::string::npos ) {{\n")
                
                if prop[i].islower():
                    f.write(f"      if( !read('{prop[i]}') ) return false;\n")
                if prop[i].isupper():
                    f.write(f"      if( !{prop[i]}() ) return false;\n")
                
                if i == len(prop) - 1:
                    f.write("      return true;\n")
                    f.write("   }\n")

        # daca neterminalul poate fii epsilon atunci este mereu adevarat
        if nullable:
            f.write("   return true; // NULLABLE\n")
        else:
            f.write("   return false; // ERROR\n")
        f.write("}\n\n")
    
    def add_main(f, starter):
        f.write("int main() {\n")
        f.write(f"   bool fin = {starter}();\n")
        f.write("   std::cout<<output;\n")
        f.write("   std::cout<<\"\\n\"<<\"finalizat = \"<<fin<<\"\\n\";")
        #f.write("   std::cout<<next=='$'?\"inputul a fost interpretat\" : \"inputul nu poate fi interpretat\";\n")
        f.write("}")
    
    open("main.cpp", 'w')
    with open("main.cpp", 'a') as f:
        add_libs(f)
        add_globals(f)
        add_function_definitions(f)
        add_helper_reader(f)
        for i in rules:
            add_parse_function(f, i)
        add_main(f, start)

#for i in rules: print(f"{i}: {rules[i]}")

print("#### FIRST(x) ####")
first_dict = get_first_dict()
for key in first_dict:
    print(f"{key} - {first_dict[key]}")

print("#### FOLLOW(x) ####")
follow_dict = get_follow_dict()
for key in first_dict:
    print(f"{key} - {follow_dict[key]}")

generate_recursive_descent_parser("aavccdd$")