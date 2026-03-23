"""
MySQL baseline SQL 导入辅助函数。
"""


def build_mysql_import_command(mysql_client, mysql_port, password, database=None):
    """
    构造 mysql 客户端导入命令。

    调用方应将 SQL 文件内容通过 stdin 传入该命令，
    避免错误地把 `source ...` 当成 SQL 传给 `-e`。
    """
    cmd = [
        mysql_client,
        "-uroot",
        f"-P{mysql_port}",
        f"-p{password}",
    ]
    masked_cmd = f"{mysql_client} -uroot -P{mysql_port} -p***"

    if database:
        cmd.append(database)
        masked_cmd = f"{masked_cmd} {database}"

    return cmd, masked_cmd
