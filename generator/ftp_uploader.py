from ftplib import FTP
from typing import Any
import yaml
from generator.app_config import AppConfig


class FTPUploader():

    def __init__(self, app_config: AppConfig) -> None:
        self._app_config = app_config

    def _load_credentials(self) -> Any:
        with open(file=self._app_config.credential_file, mode="r", encoding="utf-8") as file:
            config = yaml.safe_load(stream=file)
        return config

    def list_ftp_tree(self, ftp, remote_path="/", prefix=""):
        try:
            ftp.cwd(remote_path)
            items = ftp.nlst()
        except Exception as e:
            print(f"{prefix}[Erreur accès {remote_path}] {e}")
            return

        # Filtrer les entrées spéciales
        items = [i for i in items if i not in ('.', '..')]

        for index, item in enumerate(items):
            connector = "└── " if index == len(items)-1 else "├── "
            full_path = f"{remote_path}/{item}" if remote_path != "/" else f"/{item}"
            try:
                ftp.cwd(item)  # teste si c'est un dossier
                print(f"{prefix}{connector}[D] {full_path}")
                # Appel récursif avec indentation
                self.list_ftp_tree(ftp, remote_path=full_path, prefix=prefix + ("    " if index == len(items)-1 else "│   "))
                ftp.cwd("..")  # revenir au parent
            except Exception:
                print(f"{prefix}{connector}[F] {full_path}")

    def upload(self):

        config = self._load_credentials()['ftp']

        with FTP(config["host"]) as ftp:
        
            ftp.login(config["user"], config["password"])

            remote_dir = config.get("remote_dir", "/")

            self.list_ftp_tree(ftp=ftp, remote_path=remote_dir)

            # def ensure_dir(path):
            #     """Crée les répertoires distants si nécessaires."""
            #     parts = path.strip("/").split("/")
            #     for part in parts:
            #         try:
            #             ftp.mkd(part)
            #         except Exception:
            #             pass
            #         ftp.cwd(part)

            # ensure_dir(remote_dir)

            # for root, _, files in os.walk(local_dir):
            #     rel_path = os.path.relpath(root, local_dir)
            #     if rel_path != ".":
            #         for part in rel_path.split(os.sep):
            #             try:
            #                 ftp.mkd(part)
            #             except Exception:
            #                 pass
            #             ftp.cwd(part)

            #     for file in files:
            #         local_path = os.path.join(root, file)
            #         with open(local_path, "rb") as f:
            #             ftp.storbinary(f"STOR {file}", f)
            #             print(f"⬆️  Envoyé : {os.path.join(rel_path, file)}")

            #     ftp.cwd(remote_dir)

            #ftp.quit()