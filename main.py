import sys, bs4, requests, json, math
from bs4 import BeautifulSoup
from control.model.Database import Database as db_connection

class PokemonReader:
    def __init__(self, pokeLink) -> None:
        self.base = "https://www.pokewiki.de/"
        self.link = pokeLink
        self.data = []
        self.filename = "nomekop.csv"
        self.filepath = "./data/nomekop.json"
        pass

    def load_pokemon(self):
        print("Loading pokemon....")
        req = requests.get(self.link)
        if req.status_code == 200:
            print("Data found!")
            soup = BeautifulSoup(req.text, "html.parser")
            pokemons = soup.find('tbody').find_all('tr')
            _max = len(pokemons)
            percentage_of_one_pokemon: float = 100 / float(_max)
            for x, pokemon in enumerate(pokemons):
                pokemonData = {
                            "id": "Empty",
                            "name": "",
                            "types": [],
                            "info": None
                }

                small_image = ""
                allowed_columns = [0, 1, 2, 8]
                # Iterates columns in table
                for i, data in enumerate(pokemon.find_all('td')):
                    # Checks if i is allowed
                    if allowed_columns.__contains__(i):
                        for child in data.children:
                            if i == 0:
                                pokemonData["id"] = child.text
                            if i == 1:
                                small_image = self.base + child.find('img').attrs['src']
                            if i == 2 and type(child) == bs4.element.Tag:
                                pokemonData["name"] = child.text
                            if i == 8 and type(child) == bs4.element.Tag:
                                pokemonData["types"].append(child.text)
                
                if pokemonData["id"] != "Empty":
                    print("\rDas Programm befindet sich bei " + str(math.floor(percentage_of_one_pokemon * x)) + "/100%.", end="")
                    additionalData = self.get_additional_information(pokemonData["name"])
                    additionalData["small_image"] = small_image
                    pokemonData["info"] = additionalData
                    self.data.append(pokemonData) 
        else:
            print("Error loading data!")
            sys.exit(0)

    def get_additional_information(self, pokeName):
        req = requests.get(self.base + pokeName)
        if req.status_code == 200:
            soup = BeautifulSoup(req.text, "html.parser")
            info = {
                "appeareance": self.get_appereance(soup),
                "level_attacks": self.get_attacks(soup, "Durch Levelaufstieg"),
                "tm_attacks": self.get_attacks(soup, "Durch TM"),
                "heritability_attacks": self.get_attacks(soup, "Durch Vererbbarkeit"),
                "teacher_attacks": self.get_attacks(soup, "Durch Attacken-Lehrer"),
                "multiplier": self.get_multiplicator(soup),
                "status_values": self.get_status_values(soup),
                "image_big": self.get_bigger_image(soup)
            }
        else:
            return {}
        return info

    def get_appereance(self, soup: bs4.BeautifulSoup):
        appeareance = {
            "abilities": [],
            "weight": "",
            "category": "",
            "size": "",
            "color": ""
        }
        tbody = soup.find("table", {'class': 'right round innerround'}).find('tbody')
        for tr in list(tbody.find_all('tr')):
            aTags = list(tr.find_all('a'))
            if len(aTags) > 0:

                text = aTags[0].text
                forbode = False
                forbidden = ["Vf", "Mega", "Giga", "Ultra"]

                if text == "Fähigkeit" or text == "Fähigkeiten":
                    newAbilities = []
                    for i, abilitie_tag in enumerate(list(tr.find_all('td'))[1].find_all('a')):
                        my_tag = list(tr.find_all('td'))[1].find_all('a')[i].text
                        for f in forbidden:
                            if str(my_tag).__contains__(f) or str(my_tag).__contains__(f.lower()) or str(my_tag).__contains__(f.upper()):
                                forbode = True
                                break
                        
                            try:
                                next_tag = list(tr.find_all('td'))[1].find_all('a')[i+1].text
                                if str(next_tag).__contains__(f) or str(next_tag).__contains__(f.lower()) or str(next_tag).__contains__(f.upper()):
                                    forbode = True
                                    break
                            except:
                                pass

                        if not forbode:
                            newAbilities.append(my_tag)
                    appeareance["abilities"] = newAbilities
                elif text == "Gewicht":
                    appeareance["weight"] = list(tr.find_all('td'))[1].text.split("\n")[0].split(" ")[0] + "kg"
                elif text == "Kategorie":
                    appeareance["category"] = list(tr.find_all('td'))[1].text.split("\n")[0]
                elif text == "Größe":
                    appeareance["size"] = list(tr.find_all('td'))[1].text.split("\n")[0].split(" ")[0] + "m"
                elif text == "Farbe":
                    appeareance["color"] = list(tr.find_all('td'))[1].text.split("\n")[0].split(" ")[0]
        return appeareance

    def get_attacks(self, soup, big_tag_text: str, is_second=False):
        all_attacks = []
        if (big_tag_text.__contains__("Durch TM") or big_tag_text == "Durch Vererbbarkeit") and not is_second:
            for attack in self.get_attacks(soup, big_tag_text, is_second=True):
                all_attacks.append(attack)

        found = False
        parentElement = None
        for bigTag in soup.find_all('big'):
            if str(bigTag.text).__contains__(big_tag_text):
                if is_second and not found:
                    found = True
                    continue
                elif is_second and found:
                    parentElement = bigTag.parent
                    break
                elif not is_second:
                    parentElement = bigTag.parent
                    break
        
        if parentElement is None:
            return all_attacks

        attack_rows = parentElement.find('table').find('tbody').find('tbody').find_all('tr', {'class': 'atkrow'})
        for attack in attack_rows:
            attacke = {
                "level": "",
                "name": "",
                "type": "",
                "category": "",
                "strength": "",
                "precision": ""
            }

            keys = list(attacke.keys())
            for i, column in enumerate(attack.find_all('td')):                
                try:
                    result = attack.find_all('td')[i].text.replace("\n", "")
                except:
                    result = "None"

                attacke[keys[i]] = result
                if i == 5:
                    break
            all_attacks.append(attacke)
        return all_attacks

    def get_multiplicator(self, soup):
        multiplis = {
            '0': [],
            '0.25': [],
            '0.5': [],
            '1': [],
            '2': [],
            '4': []
        }
        multiTbody = None
        for table in soup.find_all('table'):
            try:
                if str(table.find('tbody').find('tr').find('th').text).replace(" ", "").replace("\n", "") == "Multiplikator":
                    multiTbody = table.find('tbody')
                    break
            except:
                continue

        if not multiTbody:
            return multiplis

        keys = list(multiplis.keys())
        tableRow = multiTbody.find_all('tr')[2]
        for i, data in enumerate(tableRow.find_all('td')):
            for aElement in data.find_all('a'):
                multiplis[keys[i]].append(aElement.text)
        return multiplis

    def get_status_values(self, soup):
        statusValues = {
            "health_points": 0,
            "attack": 0,
            "defense": 0,
            "special_attack": 0,
            "special_defense": 0,
            "initiative": 0,
            "sum": 0
        }
        statusTbody = None

        for table in soup.find_all('table'):
            try:
                if str(table.find('tbody').find('tr').find('th').text).replace(" ", "").replace("\n", "") == "Statuswerte":
                    statusTbody = table.find('tbody')
                    break
            except:
                continue

        if statusTbody is None:
            return statusValues

        keys = list(statusValues.keys())
        for i, tableRow in enumerate(statusTbody.find_all('tr')):
            if i == 0:
                continue
            else:
                try:
                    statusValues[keys[i-1]] = tableRow.find_all('td')[1].text.replace(" ", "").replace("\n", "")
                except:
                    statusValues[keys[i-1]] = tableRow.find_all('th')[1].text.replace(" ", "").replace("\n", "")
                    break     
        return statusValues

    def get_bigger_image(self, soup):
        src = soup.find('a', {'class': 'image'}).find('img').attrs["src"]
        src = self.base.replace("/", "") + src
        return src

    def save_to_file(self):
        print("\nCreating csv file!")
        with open(self.filepath, "w+", encoding="utf-8") as outfile:
            json.dump(self.data, outfile, indent=4)
            outfile.flush()
            outfile.close()

def main():
    # Creating new instance for pokereader
    reader = PokemonReader("https://www.pokewiki.de/Pok%C3%A9mon-Liste")
    # Loading pokemon list
    reader.load_pokemon()
    # Saving pokemon to file
    reader.save_to_file()


main()
