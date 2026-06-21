import bcrypt

def hasher_mot_passe(mot_passe):
    mot_passe_bytes = mot_passe.encode('utf-8')
    hash = bcrypt.hashpw(
        mot_passe_bytes,
        bcrypt.gensalt()
    )
    return hash.decode('utf-8')