import pandas as pd
import json


class TFTSheets :
    def __init__(self, config_file = "compos.json"):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.compos_urls = config['compos']

    def get_compo_info(self,comp :str) :
        if comp not in self.compos_urls :
            return None
        
        fichier = pd.read_csv(self.compos_urls[comp], header=None)

        info = {'nom': comp,
                'avg' : fichier.iloc[2,12],
                'winrate': fichier.iloc[2,13],
                'top4rate' : fichier.iloc[2,14]
            }
        return info
    
    def get_build_info(self,comp :str,carry :str) :
        if comp not in self.compos_urls :
            return None
        
        fichier = pd.read_csv(self.compos_urls[comp], header=None)
        items = []

        for i in range (12) :
            if pd.notna(fichier.iloc[22 + i, 1]) and fichier.iloc[22 + i,1] == carry : 
                item = {'item1' : fichier.iloc[22 + i,2],
                        'item2' : fichier.iloc[22 + i,3],
                        'item3' : fichier.iloc[22 + i,4],
                        'avg' : fichier.iloc[22 + i,5]
                }
                items.append(item)
        return items if items else None

    def get_artifact_info(self,comp :str,carry :str) :
        if comp not in self.compos_urls :
            return None
        
        fichier = pd.read_csv(self.compos_urls[comp], header=None)
        artefacts = []
        
        for i in range (12) :
            if pd.notna(fichier.iloc[51 + i,5]) and fichier.iloc[51 + i,5] == carry : 
                item = {'artefact' : fichier.iloc[51 + i,6],
                        'avg' : fichier.iloc[51 + i,7]
                }
                artefacts.append(item)
        return artefacts if artefacts else None
    
    def get_radiant_info(self,comp :str,carry :str) :
        if comp not in self.compos_urls :
            return None
        
        fichier = pd.read_csv(self.compos_urls[comp], header=None)
        radiants = []
        
        for i in range (12) :
            if pd.notna(fichier.iloc[51 + i,9]) and fichier.iloc[51 + i,9] == carry : 
                item = {'radiant' : fichier.iloc[51 + i,10],
                        'avg' : fichier.iloc[51 + i,11]
                }
                radiants.append(item)
        return radiants if radiants else None    

    def get_conditions_info(self,comp :str) :
        if comp not in self.compos_urls :
            return None
        
        fichier = pd.read_csv(self.compos_urls[comp], header=None)
        conditions = []
        
        for i in range (17) :
            if pd.notna(fichier.iloc[3 + i,11]) : 
                condi = {'condition' : fichier.iloc[3 + i,11],
                        'avg' : fichier.iloc[3 + i,12],
                        'winrate' : fichier.iloc[3 + i,13],
                        'top4rate' : fichier.iloc[3 + i,14],
                        'remarques' : fichier.iloc[3 + i,15],
                }
                conditions.append(condi)
        return conditions if conditions else None   