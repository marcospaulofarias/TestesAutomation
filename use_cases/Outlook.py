import win32com.client
from loguru import logger
from datetime import date
from utils.date_time_utils import date_str_to_int

class Outlook:
    """Clase para lidar com emails através do outlook.

    """
    def __init__(self) -> None:
        try:
            self.outlook_app = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook_app.GetNamespace("MAPI")
        except Exception as error_x:
            raise RuntimeError(
                f"Erro ao iniciar Outlook: {error_x}"
            ) from error_x

    def _get_folder(self, email_account: str, name_folder: str) -> win32com.client.CDispatch:
        """Função para selecionar uma pasta no outlook, ex: "Caixa de entrada".

        :param email_account: Nome da conta a ser usada para buscar a pasta, ex: "email@email.com".
        :param name_folder: Nome da pasta a ser usada na conta selecionada, ex "Caixa de Entrada".
        :return: Conta do outlook classic (objeto COM).
        """
        try:
            account = self._get_account_email(email_account)
            if account:
                folder = account.Folders.Item(name_folder)
                return folder
            else:
                logger.error(f'A pasta "{name_folder}" não foi selecionada')
        except Exception as error_x:
            logger.critical(f'A pasta "{name_folder}" não foi selecionada, pois a conta "{email_account}" não foi encontrada\nErro: {error_x}')
            raise RuntimeError(f'A pasta "{name_folder}" não foi selecionada, pois a conta "{email_account}" não foi encontrada\nErro: {error_x}') from error_x

    def _get_account_email(self, email_account: str) -> win32com.client.CDispatch:
        """Função para selecionar uma conta de e-mail no outlook, ex "email@email.com".
        
        :param email_account: Endereço da conta a ser selecionada no Outlook, ex "email@email.com".
        :return: Pasta do outlook (objeto COM).
        """
        try:
            account_email = self.namespace.Folders.Item(email_account)
            return account_email
        except Exception as error_x:
            logger.critical(f'E-mail "{email_account}" não encontrado\nErro: {error_x}')
            raise RuntimeError(f'E-mail "{email_account}" não encontrado\nErro: {error_x}') from error_x

    def read_emails(
            self,
            email_account: str,
            name_folder: str,
            subject: str | None = None,
            sender: str | None = None,
            unread: bool | None = None,
            has_attachments: bool | None = None,
            limit: int | None = None,
            date_outlook: str | None = None
        ) -> list[win32com.client.CDispatch]:
        """Função para ler os e-mail's de uma conta conforme filtros aplicados.
        
        :param email_account: Conta de e-mail em que serão lidos os e-mail's.
        :param name_folder: Nome da pasta em que serão lidos os e-mail's.
        :param subject: Assunto dos e-mail's pesquisados.
        :param sender: Conta de origem do recebimento dos e-mail's.
        :param unread: Apenas e-mail's não lidos.
        :param has_attachments: Apenas e-mail's que contém anexos.
        :param limit: Limite de e-mail's pesquisados, ex: 10.
        :param dateoutlook: Data de recebimento/criação do e-mail, ex "27/07/2026".
        """

        folder = self._get_folder(email_account, name_folder)

        items = folder.Items

        if items is None:
            return []

        items.Sort("[ReceivedTime]", True)

        emails = []

        for email in items:
            # print(email)

            if subject and subject.lower() not in email.Subject.lower():
                continue

            if sender and sender.lower() not in email.SenderEmailAddress.lower():
                continue

            if unread is not None and email.UnRead != unread:
                continue

            if has_attachments is not None and bool(email.Attachments.Count) != has_attachments:
                continue

            if date_outlook is not None:
                received_date = getattr(email, "ReceivedTime", None)
                creation_date = getattr(email, "CreationTime", None)
                date_email = received_date or creation_date
                date_email = date_email.date()
                day_outlook, month_outlook, year_outlook = date_str_to_int(date_outlook)
                if date_email != date(year_outlook, month_outlook, day_outlook):
                    continue

            emails.append(email)

            if limit and len(emails) >= limit:
                break

        return emails

    def send_email(
            self,
            recipients: list[str],
            subject: str,
            body: str,
            html: bool = False,
            cc: list[str] | None = None,
            bcc: list[str] | None = None,
            attachments: list[str] | None = None,
        ) -> None:
        """
        Envia um e-mail utilizando o Outlook.

        :param recipients: Lista de destinatários.
        :param subject: Assunto do e-mail.
        :param body: Corpo do e-mail.
        :param html: Se True, interpreta o corpo como HTML.
        :param cc: Lista de destinatários em cópia.
        :param bcc: Lista de destinatários em cópia oculta.
        :param attachments: Lista de caminhos dos arquivos anexos.
        """
        try:
            mail = self.outlook_app.CreateItem(0)  # olMailItem

            mail.To = ";".join(recipients)
            mail.Subject = subject

            if cc:
                mail.CC = ";".join(cc)

            if bcc:
                mail.BCC = ";".join(bcc)

            if html:
                mail.HTMLBody = body
            else:
                mail.Body = body

            if attachments:
                for file in attachments:
                    mail.Attachments.Add(file)

            mail.Send()

        except Exception as error_x:
            logger.error(f"Erro ao enviar e-mail: {error_x}")
            raise RuntimeError(
                f"Erro ao enviar e-mail: {error_x}"
            ) from error_x
