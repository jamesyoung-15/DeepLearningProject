import time
import threading
# import pdb; pdb.set_trace()
# my libraries
import gym_mariokart64.mariokart64env as mk64gym
import gym_mariokart64.m64py.m64 as m64

def main():
    # # paths
    lib_path = "./gym_mariokart64/m64py/libmupen64plus.so.2"
    plugin_path = "./gym_mariokart64/m64py/"
    rom_path = "./rom/mariokart64.n64"

    # in-game memory locations
    progress_address = 0x801644D0
    velocity_address = 0x800F6BBC
    x_pos_address = 0x800F69A4
    y_pos_address = 0x800F69AC
    z_pos_address = 0x800F69A8
    lap_address = 0x80164390


    m64py = m64.M64Py()

    # # create seperate thread for running the game
    thread1 = threading.Thread(target=m64py.run_emulator, args=(lib_path, plugin_path, rom_path))
    thread1.start()
    time.sleep(10)

    # test reading in-game memory
    while m64py.get_game_started():
        velocity = m64py.read_memory(velocity_address)
        print("Velocity: " + str(velocity))
        time.sleep(0.005)
        progress = m64py.read_memory(progress_address)
        print("Progress: " + str(progress))
        # x_pos = m64py.read_memory(x_pos_address)
        # time.sleep(0.01)
        # print("x: "+str(x_pos)+ " y: "+str(y_pos))
        # time.sleep(0.2)
        # lap = m64py.read_memory(lap_address)
        # print("lap: " + str(lap))

if __name__ == '__main__':
    main()





