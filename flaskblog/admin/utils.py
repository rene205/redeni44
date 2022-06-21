#---------------------------------------------------Verbinden zweier Dictionarys----------------------------------------------
#Die Funktion wird verwendet, um ein weiteres Produkt zu einem bestehenden Warenkorb hinzuzufügen.
#"dict1" entspricht der Session, die übergeben wird und "dict2" ist das neue Produkt.
def MagerDicts(dict1, dict2):
    if isinstance (dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance (dict1, dict) and isinstance (dict2, dict):
        return dict (list(dict1.items()) + list(dict2.items()))
    return False
#-----------------------------------------------------------------------------------------------------------------------------  

