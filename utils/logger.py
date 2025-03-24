import logging
import os 

def setup_logger(logger_name, log_file, overwrite=False ,log_level=logging.INFO):
    """
    设置一个 logger，以将日志信息写入指定的文件。

    :param logger_name: logger 的名称
    :param log_file: 要写入的日志文件路径
    :param log_level: 日志级别
    :return: logger 实例
    """
    # 创建日志目录（如果不存在的话）
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir) and log_dir:
        os.makedirs(log_dir)
    if os.path.exists(log_file):
        if not overwrite:
            print("existing log file")
            return logging.getLogger(logger_name)
        else: os.system(f"cat /dev/null > {log_file}")

    # 创建 logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)

    # 创建格式器并将其设置到处理器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 将处理器添加到 logger
    logger.addHandler(file_handler)

    return logger