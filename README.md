#Application Console – Opérateur de Production (Odoo)#
Application console Python permettant d’interagir avec un serveur Odoo : connexion, consultation des données, produits et ordres de fabrication.

#Fonctionnalités
'Connexion (F1) : authentification et affichage de la version Odoo.'

'Fiche entreprise (F2) : adresse, contact, site web.'

'Produits (F3) : liste, recherche, détail (prix, stock, catégorie).'

'Ordres de fabrication (F4) : filtrage par état, tableau synthétique.'

Mise à jour OF (F5) : modification de la quantité produite, changement d’état automatique.

#Architecture
Code
.
├── main.py
└── Odoo/
    └── OdooAPI.py

#Installation
bash
git clone https://github.com/<utilisateur>/<repo>.git
cd <repo>
python main.py
Configuration
Modifier dans main.py :

#Mainmenu
S   Configurer le serveur
F1  Connexion
F2  Fiche entreprise
F3  Produits
F4  Ordres de fabrication (+ F5)
Q   Quitter# odoo
