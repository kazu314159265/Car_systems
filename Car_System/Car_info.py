import pigpio
import time

"""
車の情報を管理するモジュール.
コメントの書き方は下記を参考にした.
https://qiita.com/simonritchie/items/49e0813508cad4876b5a

"""


class MCP3208:
    """
    ADコンバータICのMCP3208を制御するクラス.
    """
    channel = 1
    baud = 50000
    flags = 0

    def __init__(self, pi, ref_volt=3.3):
        """
        初期化処理. spiデバイスのオープンをしたりする.
        
        Parameters
        ----------
        pi : ?
            外部で作成したインスタンスを代入する変数
        ref_volt : float
            基準電圧の値
        """
        self.pi = pi
        self.ref_volt = ref_volt    #基準電圧設定
        self.hndl = pi.spi_open(self.channel, self.baud, self.flag) # デバイスオープン

    def AnalogIn(self, Channel=0):
        """
        ADコンバータから測定値を取得するメソッド. ADコンバーターのシーケンスは下記を参照.
        https://akizukidenshi.com/download/MCP3208.pdf

        Parameters
        ----------
        Channel : int
            アナログ入力をするチャンネルを指定 0-7の範囲

        Returns
        -------
        voltage : float
            基準電圧に換算した電圧値
        """
        if not 0 <= channel < 8:
            raise SPIBadChannel('channel must be between 0 and 7')  #チャンネル数が0-7の範囲にあるかチェック

        cmnd = [(0b00000110 + int(Channel / 4)), ((Channel - 4) << 6), 0]
        c, row = self.pi.spi_xfer(self.hndl, cmnd)
        voltage = (((row[1] & 0b00001111) < 8) + row[2]) * self.ref_volt / 4096
        return voltage

    def Cleanup(self):
        """
        spiデバイスをクローズする関数
        """
        self.pi.spi_close(self.hndl)


class Car_info:
    """
    車の情報を取得, 管理するクラス
    """

    speed_t_now = 0
    speed_t_last = 0
    tacho_t_now = 0
    tacho_t_last = 0
    Car_Speed = 0
    Car_tacho = 0

    def __init__(self, pi, SPEED_PULS_INPUT=6, TIRE_circumference=1.841):
        """
        初期化処理.

        Parameters
        ----------
        pi : ?
            外部で作成したインスタンスを代入する変数.
        SPEED_PULS_INPUT : int
            車速信号を入力するピン番号を指定する変数.
        TIRE_circumference : float
            タイヤの円周. 単位はメートル.
        """
        self.pi = pi
        self.SPEED_PULS_INPUT = SPEED_PULS_INPUT
        self.TIRE_circumference = TIRE_circumference

        cb = pi.callback(SPEED_PULS_INPUT, pigpio.RISING_EDGE, SpeedCallBack)

    def SpeedCallBack(gpio, level, tick):
        """
        車速信号パルスの立ち上がりエッジにより呼び出されるコールバック関数. 割り込み用関数

        Parameters
        ----------
        gpio : ?
            未検証
        level : int
            立ち上がりエッジか立ち下がりエッジかを検出するための変数
        tick : float?(未検証)
            コールバック関数が呼び出されたときのタイマーの値を取得するための変数
        """
        global speed_t_now, speed_t_last

        speed_t_last = speed_t_now
        speed_t_now = tick
        if (speed_t_last >= speed_t_now):  # if wrapped 32bit value,
            timepassed = speed_t_now - speed_t_last
        else:
            timepassed = speed_t_now + (0xffffffff + 1 - speed_t_last)

        # microseconds to seconds, per_second to per_hour
        self.Car_Speed =  (TIRE_circumference / (timepassed / 1000000)) * 3.6
    
    def TachoCallBack(gpio, level, tick):  
        """
        エンジン回転パルスの立ち上がりエッジにより呼び出されるコールバック関数. 割り込み用関数

        Parameters
        ----------
        gpio : ?
            未検証
        level : int
            立ち上がりエッジか立ち下がりエッジかを検出するための変数
        tick : float?(未検証)
            コールバック関数が呼び出されたときのタイマーの値を取得するための変数
        """
        global tacho_t_now, tacho_t_last

        tacho_t_last = tacho_t_now
        tacho_t_now = tick
        if (tacho_t_last >= tacho_t_now):  # if wrapped 32bit value,
            timepassed = tacho_t_now - tacho_t_last
        else:
            timepassed = tacho_t_now + (0xffffffff + 1 - tacho_t_last)

        # microseconds to seconds, per_second to per_hour
        self.Car_tacho =  (1 / (timepassed / 1000000)) * 60
        

