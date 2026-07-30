import os
import psutil
from loguru import logger
from use_cases.PrintAutomation import PrintAutomation
from utils.config import load_apps_config
import subprocess

def kill_program_by_name(process_name: str, timeout: float = 5, force: bool = True, process_id: str = None, process_type: str = None, process_machine: str = None) -> bool:
    """Função para finalizar um programa pelo nome do processo (útil para apps UWP/stub como CalculatorApp.exe)
    :process_name: Nome do processo a ser finalizado (ex: 'CalculatorApp.exe')
    :timeout: Tempo (s) a aguardar o processo encerrar após o terminate/kill
    :force: Se True, força o encerramento (.kill()) dos processos que não fecharem no timeout"""
    printautomation = PrintAutomation(process_id=process_id, process_type=process_type, process_machine=process_machine)
    try:
        procs = [p for p in psutil.process_iter(['name']) if p.info['name'] == process_name]
        if not procs:
            logger.warning(f'Nenhum processo "{process_name}" encontrado em execução')
            return False
        for proc in procs:
            proc.terminate()
        _, alive = psutil.wait_procs(procs, timeout=timeout)
        if alive and force:
            for proc in alive:
                proc.kill()
            psutil.wait_procs(alive, timeout=timeout)
        return True
    except Exception as error_x:
        printautomation.print_error()
        logger.critical(f'O processo "{process_name}" não pôde ser finalizado\nError: {error_x}')
        raise RuntimeError(f'O processo "{process_name}" não pôde ser finalizado\nError: {error_x}') from error_x


def kill_all(app_keys: list = None, apps_config: dict = None, process_id: str = None, process_type: str = None, process_machine: str = None) -> bool:
    """Finaliza todos os processos listados na configuração de apps.

    :param app_keys: Lista de chaves de apps a finalizar. Se None, usa todas as chaves do config.
    :param apps_config: Config já carregada (evita ler o arquivo novamente).
    :returns: True se a operação foi executada (não garante que havia processos).
    """
    if apps_config is None:
        apps_config = load_apps_config()
    keys = app_keys or list(apps_config.keys())
    any_killed = False
    for k in keys:
        cfg = apps_config.get(k) or {}
        proc_name = cfg.get("name_of_process") or os.path.basename(cfg.get("name_of_program") or "")
        if not proc_name:
            logger.warning(f"Nenhum processo associado à app '{k}' para finalizar")
            continue
        try:
            killed = kill_program_by_name(process_name=proc_name, process_id=process_id, process_type=process_type, process_machine=process_machine)
            any_killed = any_killed or bool(killed)
        except psutil.AccessDenied:
            result_kill = subprocess.run(["taskkill", "F", "IM", proc_name],
                           capture_output=True,
                           text=True,
                           timout=10,)
            if result_kill.return_code == 0:
                return True
            else:
                logger.critical(f'O programa "{proc_name}" não pôde ser finalizado. Verificar possível erro.')
                raise RuntimeError(f'O programa "{proc_name}" não pôde ser finalizado. Verificar possível erro.')
        except Exception:
            # já logado em kill_program_by_name
            continue
    # Após finalizar os processos listados, também finalizar quaisquer processos
    # Python em execução (exceto o processo atual) para garantir que a automação
    # não continue em caso de falha.
    # Controla se processos Python devem ser finalizados via variável de ambiente.
    kill_py_flag = os.getenv("KILL_PY_ON_ERROR", "false").lower() in ("1", "true", "yes")
    if not kill_py_flag:
        logger.info('KILL_PY_ON_ERROR is not enabled; skipping Python process termination')
    else:
        try:
            current_pid = os.getpid()
            python_names = {"python.exe", "pythonw.exe", "python"}
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    name = (proc.info.get('name') or '').lower()
                    if proc.info.get('pid') == current_pid:
                        continue
                    # Verifica nomes conhecidos de processos Python
                    if any(pn in name for pn in python_names):
                        logger.info(f'Terminando processo Python: pid={proc.pid} name={proc.info.get("name")}')
                        proc.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            # Aguarda encerramento e força kill se necessário
            _, alive = psutil.wait_procs([p for p in psutil.process_iter(['pid', 'name']) if p.info.get('pid') != current_pid and (p.info.get('name') or '').lower() in python_names], timeout=5)
            if alive:
                for p in alive:
                    try:
                        p.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                psutil.wait_procs(alive, timeout=5)
        except Exception as error_x:
            logger.warning(f'Erro ao tentar finalizar processos Python: {error_x}')

    return any_killed
