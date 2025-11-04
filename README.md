# PyArchiver (par xjapan)

Un outil de compression/décompression simple et avancé, écrit en Python avec une interface graphique Tkinter.

![Capture d'écran de l'application](https://i.imgur.com/IAj2h8r.png)


---

### ✨ Fonctionnalités

* **Compression** aux formats ZIP, TAR et TAR.GZ (Gzip).
* **Décompression** d'archives (ZIP, TAR, TAR.GZ).
* **Cryptage AES** avec mot de passe pour les archives ZIP.
* **Interface graphique claire** avec suivi de la progression en temps réel.
* **Personnalisation** :
    * Choix du thème de l'application.
    * Choix de la police et de la taille (nécessite un redémarrage).
* **Sauvegarde des préférences** (thème et police).

---

### 🚀 Installation (Utilisateurs)

Rendez-vous dans la section **[Releases](https://github.com/xjapan007/PyArchiver/releases)** de ce dépôt pour télécharger la version adaptée à votre système.

#### Pour Windows
1.  Téléchargez le fichier `PyArchiver-Setup.exe`.
2.  Lancez l'installeur et suivez les instructions.

#### Pour Linux (Binaire)
1.  Téléchargez le binaire `PyArchiver_by_xjapan`.
2.  Ouvrez un terminal dans votre dossier de téléchargement.
3.  Rendez le fichier exécutable :
    ```bash
    chmod +x PyArchiver_by_xjapan
    ```
4.  Lancez l'application :
    ```bash
    ./PyArchiver_by_xjapan
    ```

---

### 💻 Lancement (pour développeurs)

Si vous souhaitez lancer le projet depuis le code source :

1.  Clonez ce dépôt :
    ```bash
    git clone [https://github.com/xjapan007/PyArchiver.git](https://github.com/xjapan007/PyArchiver.git)
    cd PyArchiver
    ```
2.  **Important (Linux uniquement)** : Assurez-vous d'avoir `python3-tk` :
    ```bash
    sudo apt update && sudo apt install python3-tk
    ```
3.  Créez un environnement virtuel et activez-le :
    * (Windows): `py -m venv venv` et `venv\Scripts\activate`
    * (Linux/macOS): `python3 -m venv venv` et `source venv/bin/activate`

4.  Installez les dépendances :
    ```bash
    pip install ttkthemes pyzipper pycryptodomex
    ```
5.  Lancez l'application :
    ```bash
    python PyArchiver.py
    ```

---

### ❤️ Soutenir le projet

Si ce projet vous est utile et que vous souhaitez me remercier, vous pouvez m'offrir un café !

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/P5P21NKY2H)

---

### 📄 Licence

Ce projet est distribué sous la **Licence MIT**.