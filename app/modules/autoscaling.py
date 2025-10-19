# 使用 #@DESC 描述此模組的用途
# 模組對於基礎設施定義檔處理流程與參數解析說明描述於 desc 函數
#@DESC Simple module structure, and run standard command.

# Import libraries
from libs.docker import Service
# Declare variable
# Declare function
def main():
    """
    ISA 系統不會呼叫該函數，此函數應用於單獨執行時，用來測試模組內容
    """

def desc():
    """
    用於描述當前模組對配置內容的處理規則。
    """
    print("This module is run for standard command.")

def exec(config):
    """
    模組執行時最後呼叫的函數，可在此執行配置檔中無特定對應函數的內容
    """
    print("Execute module with config.")
    s = Service(config, exec.__module__)
    s.run()

def deploy(service, config):
    """
    執行服務容器部屬調整，若配置檔存在關鍵字 deploy，依據其參數執行相應調整
    """
    ## Declare variable
    conf = service.config
    mgr = service.manager
    ## Retrieve service total amount.
    CMD = f"{mgr.manager_cmd} compose --file {mgr.manager_conf} --env-file {mgr.manager_env} ps -a | grep {conf['container']['name']} | wc -l"
    count = int(mgr._call_command(command=CMD, isPrint=False).strip())
    ## Check scale mode, to up or down.
    scale = 'up'
    replicas = {}
    if 'scale' in config:
        scale = config['scale']
    if 'replicas' in config:
        replicas = config['replicas']
    match scale:
        case 'up':
            count+=1
            max = int(replicas['max']) if 'max' in replicas else count + 1
            count = count if count < max else max
            CMD = f"{mgr.manager_cmd} compose --file {mgr.manager_conf} --env-file {mgr.manager_env} up -d --scale {conf['container']['name']}={count}"
            mgr._call_command(command=CMD)
        case 'down':
            count-=1
            min = int(replicas['min']) if 'min' in replicas else 1
            count = count if count >= min else min
            CMD = f"{mgr.manager_cmd} compose --file {mgr.manager_conf} --env-file {mgr.manager_env} up -d --scale {conf['container']['name']}={count}"
            mgr._call_command(command=CMD)
        case _:
            print(f"Error: unknown scale command {scale}")

# Python entrypoint program
if __name__ == '__main__':
    main()
