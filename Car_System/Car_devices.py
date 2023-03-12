from time import sleep

import pigpio


class MCP3208:
    """
    ADコンバータICのMCP3208を制御するクラス.MCP3208はMicrochip社の12bitのADコンバーターSPIインターフェースで制御できる.
    ADコンバーターの取扱説明書,及びシーケンスは下記を参照.
    https://akizukidenshi.com/download/MCP3208.pdf
    """

    channel = 1
    baud = 50000
    flags = 0

    def __init__(self, pi, ref_volt=3.3):
        """
        初期化処理. spiデバイスのオープンをしたりする.

        Parameters
        ----------
        pi : class
            外部でインスタンス化したpigpio.piのクラスオブジェクトを代入する変数
        ref_volt : float
            基準電圧の値
        """
        self.pi = pi
        self.ref_volt = ref_volt  # 基準電圧設定
        self.hndl = pi.spi_open(self.channel, self.baud, self.flags)  # デバイスオープン

    def AnalogIn(self, Channel=0):
        """
        ADコンバータから測定値を取得するメソッド.

        Parameters
        ----------
        Channel : int
            アナログ入力をするチャンネルを指定 0-7の範囲

        Returns
        -------
        voltage : float
            コンストラクタで設定した基準電圧に換算した電圧値
        """
        if not 0 <= Channel < 8:
            raise SPIBadChannel(
                "channel must be between 0 and 7"
            )  # チャンネル数が0-7の範囲にあるかチェック

        cmnd = [(0b00000110 + int(Channel / 4)), ((Channel & 0b00000011) << 6), 0]
        c, row = self.pi.spi_xfer(self.hndl, cmnd)
        voltage = (((row[1] & 0b00001111) << 8) + row[2]) * self.ref_volt / 4096
        return voltage

    def Cleanup(self):
        """
        spiデバイスをクローズする関数
        """
        self.pi.spi_close(self.hndl)


class NJU72343:
    """
    8ch電子ボリューム NJU72343を操作するクラス.
    取扱説明書,及びシーケンスは下記を参照。
    https://akizukidenshi.com/download/ds/njr/NJU72343_J.pdf
    """

    def __init__(self, pi, DATA_pin, CLOCK_pin, Chip_Address=0x80):
        """
        初期化処理. 電子ボリュームICに使用するピンなどを指定.

        Parameters
        ----------
        pi : class
            外部でインスタンス化したpigpio.piのクラスオブジェクトを代入する変数
        ref_volt : float
            基準電圧の値
        """

        self.write_wate_time = 4

        self.pi = pi
        self.DATA_pin = DATA_pin
        self.CLOCK_pin = CLOCK_pin
        self.Chip_Address = Chip_Address

        pi.set_mode(DATA_pin, pigpio.OUTPUT)
        pi.set_mode(CLOCK_pin, pigpio.OUTPUT)

        self.pi.write(self.DATA_pin, 0)
        self.pi.write(self.CLOCK_pin, 0)

    def write(self, addr, data):
        """
        チップにデータを書き込むメソッド
        """

        self.pi.write(self.DATA_pin, 1)
        sleep(self.write_wate_time)
        # 通信初期状態

        self.pi.write(self.DATA_pin, 0)
        sleep(self.write_wate_time * 2)
        self.pi.write(self.CLOCK_pin, 1)
        sleep(self.write_wate_time * 2)
        self.pi.write(self.DATA_pin, 0)

