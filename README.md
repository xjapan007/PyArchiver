# PyArchiver_by_xjapan

Un outil de compression/décompression simple et avancé, écrit en Python avec une interface graphique Tkinter.

![Capture d'écran de l'application](https://i.imgur.com/IAj2h8r.png)


---

### ✨ Fonctionnalités

* **Compression** aux formats ZIP, TAR et TAR.GZ (Gzip).
* **Décompression** d'archives (ZIP, TAR, TAR.GZ).
* **Cryptage AES** avec mot de passe pour les archives ZIP.
* **Interface graphique claire** avec suivi de la progression en temps réel (ne gèle pas).
* **Personnalisation** complète :
    * Choix du thème de l'application.
    * Choix de la police et de la taille.
* **Sauvegarde des préférences** : L'application mémorise votre thème et votre police.

---

### 🛠️ Technologies utilisées

* **Python 3**
* **Tkinter** (bibliothèque graphique standard)
* **`ttkthemes`** (pour les thèmes de l'interface)
* **`pyzipper`** (pour la gestion du cryptage AES des ZIP)
* **`tarfile`** (bibliothèque standard pour les archives TAR)

---

### 🚀 Installation et Lancement

1.  Clonez ce dépôt (ou téléchargez le ZIP) :
    ```bash
    git clone [https://github.com/xjapan007/PyArchiver.git](https://github.com/xjapan007/PyArchiver.git)
    cd PyArchiver-GUI
    ```

2.  Installez les dépendances Python requises :
    ```bash
    pip install ttkthemes pyzipper pycryptodomex
    ```

3.  Lancez l'application :
    ```bash
    python compress_tool.py
    ```

---

### ❤️ Soutenir le projet

Si ce projet vous est utile et que vous souhaitez me remercier, vous pouvez m'offrir un café !

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/P5P21NKY2H)

---

### 📄 Licence

Ce projet est distribué sous la **Licence MIT**. Voir le fichier `LICENSE` pour plus de détails.