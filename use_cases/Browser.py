from time import sleep
from re import sub
from random import uniform
from pyautogui import keyDown
from use_cases.UiAutomationClass import UiAutomationClass
from use_cases.Initializator import Initializator
from use_cases.PathManager import PathManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from loguru import logger
from utils.serial_killer import kill_program_by_name, kill_all
from use_cases.PrintAutomation import PrintAutomation
import requests

class Browser(UiAutomationClass):
    """Classe para automação web usando UiAutomation e Selenium.

    Esta classe permite superar limitações do Selenium com uiautomation e vice-versa.

    :param process_id: Identificador do processo para logs e rastreamento.
    :param process_type: Tipo do processo para logs e rastreamento.
    :param process_machine: Nome da máquina para logs e rastreamento.
    """
    BY_METHODS = {
        "name": By.NAME,
        "class_name": By.CLASS_NAME,
        "xpath": By.XPATH,
        "id": By.ID,
        "css_selector": By.CSS_SELECTOR,
        "tag_name": By.TAG_NAME,
        "link_text": By.LINK_TEXT,
        "partial_link_text": By.PARTIAL_LINK_TEXT,
    }

    def __init__(self, process_id: str = None, process_type: str = None, process_machine: str = None, headless: bool = False) -> None:
        super().__init__(process_id=process_id, process_type=process_type, process_machine=process_machine)
        self.initializator = Initializator(process_id=process_id, process_type=process_type, process_machine=process_machine)
        self.pathmanager = PathManager()
        self.driver = None
        self.by_methods = dict(self.BY_METHODS)
        self.process_id = process_id
        self.process_type = process_type
        self.process_machine = process_machine
        self.printautomation = PrintAutomation(process_id=self.process_id, process_type=self.process_type, process_machine=self.process_machine)
        self.headless = headless
        kill_program_by_name(process_name="msedge")

    def _open_browser(self) -> None:
        """Função privada para iniciar o browser edge.
        Nesta função já está incluída a verificação para evitar duplicidade de navegadores."""
        try:
            self.close_browser()
            options = webdriver.EdgeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--start-maximized")
            if self.headless:
                # Modo headless
                options.add_argument("--headless=new")

                # Recomendações
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
            self.driver = webdriver.Edge(options=options)
        except Exception as error_x:
            self.printautomation.print_error()
            logger.critical(f'Erro ao abrir o navegador\nERROR: {error_x}')
            kill_all()
            raise RuntimeError("Erro ao abrir o navegador") from error_x

    def _verify_site_connection(self, url_site: str, try_repetitions: int = 3, time_new_retry: float = 1.0) -> bool:
        last_error = None
        for _ in range(try_repetitions):
            try:
                response = requests.get(url_site, timeout=10)
                if response.status_code == 200:
                    return True
            except Exception as error_x:
                last_error = error_x
                logger.warning(f'Erro ao tentar acessar o site {url_site}: {error_x}')
            sleep(time_new_retry)
        self.printautomation.print_error()
        logger.critical(f'Não foi possível acessar o site {url_site} após {try_repetitions} tentativas')
        kill_all()
        raise RuntimeError(
            f'Não foi possível acessar o site {url_site} após {try_repetitions} tentativas'
        ) from last_error

    def get_site(self, url_site: str = 'https://www.google.com') -> None:
        """Acessa uma página web a partir de uma URL completa.

        Exemplo correto: https://www.google.com
        Exemplo incorreto: www.google.com

        :param url_site: URL completa para ser acessada.
        """
        if not self._verify_site_connection(url_site=url_site):
            self.printautomation.print_error()
            logger.critical(f'Não foi possível acessar o site {url_site}')
            kill_all()
            raise RuntimeError(f'Não foi possível acessar o site {url_site}')
        self._open_browser()
        if self.driver:
            self.driver.get(url=url_site)

    def close_browser(self) -> None:
        """Fecha o navegador.

        Caso haja erro ao fechar via driver, tenta encerrar o processo pelo subprocesso.
        A função não é privada para permitir encerramento externo quando necessário.
        """
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as error_x:
                self.printautomation.print_error()
                logger.critical(f'Erro ao fechar o navegador\nError: {error_x}')
                kill_all()
                raise RuntimeError('Erro ao fechar o navegador') from error_x
        else:
            try:
                kill_program_by_name(process_name="msedge.exe", process_id=self.process_id, process_type=self.process_type, process_machine=self.process_machine)
                self.driver = None
            except Exception as error_x:
                self.printautomation.print_error()
                logger.critical(f'Erro ao fechar o navegador pelo subprocesso\nError: {error_x}')

    def keyboard(
        self,
        element,
        word: str,
        key_down: bool,
        just_numbers: bool,
        verify: bool = True,
        clean: bool = True,
        word_to_remove: str = None,
        max_attempts: int = 3,
    ) -> None:
        """Interage com campos de texto editáveis.

        :param element: Elemento web de texto editável.
        :param word: Palavra ou frase para enviar ao elemento.
        :param key_down: Se True, envia tecla direita após cada caractere.
        :param just_numbers: Se True, verifica apenas números no valor final.
        :param verify: Se True, verifica se o valor final está correto.
        :param clean: Se True, limpa o campo antes de enviar o valor.
        :param word_to_remove: Palavra a ser removida de `word` antes da verificação.
        :param max_attempts: Número máximo de tentativas de preenchimento antes de falhar.
        """
        if element is None:
            kill_all()
            raise ValueError("Elemento obrigatório para keyboard()")

        attempt = 0
        while attempt < max_attempts:
            attempt += 1

            if clean:
                element.clear()

            for caract in word:
                sleep(uniform(0.5, 1.5))
                element.send_keys(caract)
                if key_down is True:
                    keyDown('right')
                    element.click()

            if not verify:
                return

            current_value = element.get_attribute('value') or ""
            expected_value = word

            if just_numbers:
                current_value = sub(r"\D", "", current_value)
                expected_value = sub(r"\D", "", word)
            elif word_to_remove is not None:
                current_value = current_value.replace(word_to_remove, "")
                expected_value = word.replace(word_to_remove, "")

            if current_value == expected_value:
                return

            logger.warning(
                f"keyboard(): tentativa {attempt} falhou, valor atual='{current_value}' vs esperado='{expected_value}'"
            )
            sleep(0.5)

        self.printautomation.print_error(element_to_print=element)
        kill_all()
        raise RuntimeError(
            f"Não foi possível preencher o campo corretamente após {max_attempts} tentativas"
        )

    def element_response(self, method: By, element_id: str, message_success: str, message_error: str, repetitions: int=30, element: any = None, click: bool = False, update: bool = False):
        """Tenta capturar um elemento web repetidamente.

        :param method: Método usado para identificar o elemento [By.NAME, By.CLASS_NAME, By.XPATH, etc.].
        :param element_id: Identificador do elemento, exemplo: password, table, name_id_1.
        :param message_success: Mensagem exibida ao capturar o elemento com sucesso.
        :param message_error: Mensagem exibida em caso de erro ao capturar o elemento.
        :param repetitions: Número de tentativas para capturar o elemento.
        :param element: Elemento pai a partir do qual a captura é feita, se aplicável.
        :param click: Se True, clica no elemento assim que capturado.
        :param update: Se True, atualiza a página a cada 20 tentativas.
        :returns: O elemento capturado ou True se o clique for realizado.
        :raises RuntimeError: Quando o elemento não é encontrado após as tentativas.
        """
        last_error = None
        if element is None:
            for _ in range(repetitions):
                if update and (_ + 1) % 20 == 0:
                    self.driver.refresh()
                    logger.info('Atualizou a página')
                logger.info(f'TENTATIVA {_ + 1} de {repetitions}')
                try:
                    if click:
                        self.driver.find_element(method, element_id).click()
                        logger.info(message_success)
                        return True
                    result = self.driver.find_element(method, element_id)
                    logger.info(message_success)
                    return result
                except Exception as error_x:
                    last_error = error_x
                    logger.error(f'{message_error}: {error_x}')
                sleep(1)
        else:
            for _ in range(repetitions):
                logger.info(f'TENTATIVA {_ + 1} de {repetitions}')
                try:
                    result = element.find_element(method, element_id)
                    logger.info(message_success)
                    return result
                except Exception as error_x:
                    last_error = error_x
                    logger.error(f'{message_error}: {error_x}')
                sleep(1)
        logger.critical(f'Não foi possível capturar o elemento após {repetitions} tentativas')
        self.printautomation.print_error()
        kill_all()
        raise RuntimeError(f'Não foi possível capturar o elemento após {repetitions} tentativas') from last_error
    
    def elements_response(self, method: By, element_id: str, message_success: str, message_error: str, repetitions: int=30, element: any = None):
        """Tenta capturar uma ou mais ocorrências de um elemento web repetidamente.

        :param method: Método usado para identificar o(s) elemento(s) [By.NAME, By.CLASS_NAME, By.XPATH, etc.].
        :param element_id: Identificador do(s) elemento(s), exemplo: password, table, name_id_1.
        :param message_success: Mensagem exibida ao capturar o(s) elemento(s) com sucesso.
        :param message_error: Mensagem exibida em caso de erro ao capturar o(s) elemento(s).
        :param repetitions: Número de tentativas para capturar o(s) elemento(s).
        :param element: Elemento pai a partir do qual a captura é feita, se aplicável.
        :returns: Lista de elementos capturados.
        :raises RuntimeError: Quando nenhum elemento é encontrado após as tentativas.
        """
        last_error = None
        if element is None:
            for _ in range(repetitions):
                logger.info(f'TENTATIVA {_ + 1} de {repetitions}')
                try:
                    result = self.driver.find_elements(method, element_id)
                    if result:
                        logger.info(message_success)
                        return result
                    last_error = ValueError('Nenhum elemento encontrado')
                    logger.error(f'{message_error}: Nenhum elemento encontrado')
                except Exception as error_x:
                    last_error = error_x
                    logger.error(f'{message_error}: {error_x}')
                sleep(1)
        else:
            for _ in range(repetitions):
                logger.info(f'TENTATIVA {_ + 1} de {repetitions}')
                try:
                    result = element.find_elements(method, element_id)
                    if result:
                        logger.info(message_success)
                        return result
                    last_error = ValueError('Nenhum elemento encontrado')
                    logger.error(f'{message_error}: Nenhum elemento encontrado')
                except Exception as error_x:
                    last_error = error_x
                    logger.error(f'{message_error}: {error_x}')
                sleep(1)
        logger.critical(f'Não foi possível capturar o(s) elemento(s) após {repetitions} tentativas')
        self.printautomation.print_error()
        kill_all()
        raise RuntimeError(f'Não foi possível capturar o(s) elemento(s) após {repetitions} tentativas') from last_error
    
    def try_click(self, element, repetitions: int = 30) -> bool:
        """Tenta várias vezes clicar em um elemento web.

        :param element: Elemento web para clicar.
        :param repetitions: Número de tentativas para clicar no elemento.
        :returns: True se o clique foi realizado, False caso contrário.
        """
        for _ in range(repetitions):
            logger.info(f'TENTATIVA {_ + 1} de {repetitions}')
            try:
                element.click()
                logger.info('Clique realizado com sucesso')
                return True
            except Exception as error_x:
                logger.error(f'Erro ao tentar clicar no elemento: {error_x}')
            sleep(1)
        logger.critical(f'Não foi possível clicar no elemento após {repetitions} tentativas')
        self.printautomation.print_error()
        kill_all()
        raise RuntimeError(f'Não foi possível clicar no elemento após {repetitions} tentativas') from error_x
