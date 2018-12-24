GPIO_PIN_F = 1
GPIO_PIN_S = 2
GPIO_PIN_G = 4

gpio.mode(GPIO_PIN_F,gpio.INT)
gpio.mode(GPIO_PIN_S,gpio.INT)
gpio.mode(GPIO_PIN_G,gpio.OUTPUT) 

global_status = 0
local http_post = "http_post.lua"

function interrupt_f(level, stamp)
gpio.trig(GPIO_PIN_F)
sensor_f = gpio.read(GPIO_PIN_F)
sensor_s = gpio.read(GPIO_PIN_S)
    if (sensor_f==1) then
        global_status = 0
    end
dofile(http_post)
gpio.write(GPIO_PIN_G, global_status)
tmr.delay(700000)
    print('level:',level)
    print('stamp(us):',stamp)
print('interrupt on pin:', GPIO_PIN_F)
print('global status:', global_status)
gpio.trig(GPIO_PIN_F,"both", interrupt_f)
end

function interrupt_s(level, stamp)
gpio.trig(GPIO_PIN_S)
sensor_f = gpio.read(GPIO_PIN_F)
sensor_s = gpio.read(GPIO_PIN_S)
    if (sensor_s==1) then
        global_status = 1
    end
dofile(http_post)
gpio.write(GPIO_PIN_G, global_status)
tmr.delay(700000)
    print('level:',level)
    print('stamp(us):',stamp)
print('interrupt on pin:', GPIO_PIN_S)
print('global status:', global_status)
gpio.trig(GPIO_PIN_S,"both", interrupt_s)
end

gpio.trig(GPIO_PIN_F,"both", interrupt_f)
gpio.trig(GPIO_PIN_S,"both", interrupt_s)
