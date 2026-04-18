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

def first(c : str):
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

for i in rules: print(f"{i}: {rules[i]}")

print("#### FIRST(x) ####")
first_dict = get_first_dict()
for key in first_dict:
    print(f"{key} - {first_dict[key]}")

print("#### FOLLOW(x) ####")
follow_dict = get_follow_dict()
for key in first_dict:
    print(f"{key} - {follow_dict[key]}")