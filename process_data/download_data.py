import cdsapi
from subprocess import call
import calendar


def idmDownloader(task_url, folder_path, file_name):
    """
    IDM下载器
    :param task_url: 下载任务地址
    :param folder_path: 存放文件夹
    :param file_name: 文件名
    :return:
    """
    # IDM安装目录
    idm_engine = "C:\\Users\\Administrator\\Desktop\\Internet Download Manager\\IDMan.exe"
    # 将任务添加至队列
    call([idm_engine, '/d', task_url, '/p', folder_path, '/f', file_name, '/a'])
    # 开始任务队列
    call([idm_engine, '/s'])


if __name__ == '__main__':
    c = cdsapi.Client()  # 创建用户

    # 数据信息字典
    dic = {
        'version': '1_1',
        'format': 'zip',
        'variable': '2m_temperature',
        'statistic': '24_hour_mean',
        'year': '',
        'month': '',
        'day': [],
    }

    # 通过循环批量下载1979年到2020年所有月份数据
    for y in range(2001, 2015):  # 遍历年
        for m in range(1, 13):  # 遍历月
            # 将年、月、日更新至字典中
            day_num = calendar.monthrange(y, m)[1]  # 根据年月，获取当月日数
            dic['year'] = str(y)
            dic['month'] = str(m).zfill(2)
            dic['day'] = [str(d).zfill(2) for d in range(1, day_num + 1)]

            r = c.retrieve('sis-agrometeorological-indicators', dic, )  # 文件下载器
            url = r.location  # 获取文件下载地址
            # 文件夹
            path = 'D:\\Drought_and_heat_wave_coupling\\data\\Tmean_data\\' + str(y)
            filename = str(y) + str(m).zfill(2) + '.zip'  # 文件名
            idmDownloader(url, path, filename)  # 添加进IDM中下载

    # c = cdsapi.Client()
    #
    # r = c.retrieve(
    #     'satellite-land-cover',
    #     {
    #         'variable': 'all',
    #         'format': 'zip',
    #         'year': '2014',
    #         'version': 'v2.0.7cds',
    #     }, )
    # url = r.location
    # path = 'D:\\landcover'
    # filename = str(2014) + '.zip'  # 文件名
    # idmDownloader(url, path, filename)  # 添加进IDM中下载