import win32com.client
from loguru import logger

class Outlook:
    """Clase para lidar com emails através do outlook.
    
    :param outlook_app: Aplicação outlook classic.
    :param namespace: Aplicação outlook classic usando protocolo "MAPI".
    :param account_email: Conta email usada ex: "email@email.com".
    :param folder: Pasta de email trabalhada, ex: "Caixa de entrada".
    """
    def __init__(self) -> None:
        try:
            self.outlook_app = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook_app.GetNamespace("MAPI")
        except Exception as error_x:
            raise RuntimeError(
                f"Erro ao iniciar Outlook: {error_x}"
            ) from error_x
        self.account_email = None
        self.folder = None

    def _get_folder(self, email_account: str, name_folder: str) -> None:
        """Função para selecionar uma pasta no outlook, ex: "Caixa de entrada".

        :param email_account: Nome da conta a ser usada para buscar a pasta, ex: "email@email.com".
        :param name_folder: Nome da pasta a ser usada na conta selecionada, ex "Caixa de Entrada".
        :returns:
        """
        try:
            if self._get_account_email(email_account):
                self.folder = self.account_email.Folders.Item(name_folder)
                return self.folder
            else:
                logger.error(f'A pasta "{name_folder}" não foi selecionada')
        except Exception as error_x:
            logger.error(f'A pasta "{name_folder}" não foi selecionada, pois a conta "{email_account}" não foi encontrada\nErro: {error_x}')

    def _get_account_email(self, email_account: str) -> bool:
        """Função para selecionar uma conta de e-mail no outlook, ex "email@email.com".
        
        :param email_account: Endereço da conta a ser selecionada no Outlook, ex "email@email.com".
        :returns:
        """
        try:
            self.account_email = self.namespace.Folders.Item(email_account)
            return True
        except Exception as error_x:
            logger.error(f'E-mail "{email_account}" não encontrado\nErro: {error_x}')
            return False

    def _back_to_default(self) -> None:
        """Função para voltar self.account_email e self.folder a ser None após finalização de alguma operação, assim é evitado um bug."""
        self.account_email = None
        self.folder = None

    def read_emails(self, email_account: str, name_folder: str) -> list[win32com.client.CDispatch]:
        """Função para ler emails de uma pasta em uma determinada conta de email.
        
        :param email_account: Conta onde será encontrada a pasta, ex "email@email.com".
        :param name_folder: Nome da pasta de onde os e-mail's serão lidos, ex: "Caixa de Entrada".
        :returns Lista de bjetos COM.:
        """
        self._get_folder(email_account=email_account, name_folder=name_folder)
        if self.folder:
            new_folder = self.folder
            self._back_to_default()
            return [email for email in new_folder.Items]
        return []

if __name__ == '__main__':
    outlook = Outlook()
