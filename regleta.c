#include <stdio.h>
#include <stdlib.h>
#include "pico/stdlib.h"
#include "hardware/adc.h"
#include "hardware/gpio.h"

#define LED_ON 22
#define C0 0
#define C1 1
#define C2 2
#define C3 3
#define ANALOG_PIN 26

#define NUM_SENSORS 16
#define NUM_SAMPLES 10
#define DISPLAY_TIME 30
#define SAMPLE_DELAY_MS 100
#define ADC_MAX 4095

uint16_t min_vals[NUM_SENSORS] = {0};
uint16_t max_vals[NUM_SENSORS] = {0};
float sensor_positions[NUM_SENSORS] = {-45, -39, -33, -27, -21, -15, -9, -3, 3, 9, 15, 21, 27, 33, 39, 45};
float last_position = 0.0f;
bool calibrated = false;

void select_sensor(uint8_t index) {
    gpio_put(C3, (index >> 3) & 1);
    gpio_put(C2, (index >> 2) & 1);
    gpio_put(C1, (index >> 1) & 1);
    gpio_put(C0, index & 1);
}

uint16_t read_sensor() {
    return adc_read();
}

void read_all_sensors(uint16_t *values) {
    for (int i = 0; i < NUM_SENSORS; i++) {
        select_sensor(i);
        sleep_us(10);
        values[i] = read_sensor();
    }
}

uint16_t calibrate_value(uint16_t raw_val, uint8_t sensor_idx) {
    uint16_t min_val = min_vals[sensor_idx];
    uint16_t max_val = max_vals[sensor_idx];
    
    if (max_val <= min_val) {
        return 0;
    }

    float cal_val = (float)(raw_val - min_val) * (float)ADC_MAX / (float)(max_val - min_val);

    if (cal_val < 0.0f) return 0;
    if (cal_val > (float)ADC_MAX) return ADC_MAX;
    return (uint16_t)cal_val;
}


void activity1() {
    uint32_t start_time = to_ms_since_boot(get_absolute_time());
    uint16_t values[NUM_SENSORS];
    
    printf("INICIANDO ACTIVIDAD 1 - LECTURA DE VALORES CRUDOS\n");
    
    while (to_ms_since_boot(get_absolute_time()) - start_time < DISPLAY_TIME * 1000) {
        read_all_sensors(values);
        
        printf("RAW");
        for (int i = 0; i < NUM_SENSORS; i++) {
            printf(",%d", values[i]);
        }
        printf("\n");
        
        sleep_ms(SAMPLE_DELAY_MS);
    }
}

void activity2() {
    uint16_t values[NUM_SENSORS];
    uint32_t start_time;
    
    printf("COLOCAR EN SUPERFICIE BLANCA - CAPTURANDO MINIMOS\n");
    sleep_ms(5000);

    for (int i = 0; i < NUM_SENSORS; i++) {
        min_vals[i] = 0;
    }
    
    for (int sample = 0; sample < NUM_SAMPLES; sample++) {
        read_all_sensors(values);
        for (int i = 0; i < NUM_SENSORS; i++) {
            min_vals[i] += values[i];
        }
        sleep_ms(100);
    }
    
    for (int i = 0; i < NUM_SENSORS; i++) {
        min_vals[i] /= NUM_SAMPLES;
    }

    start_time = to_ms_since_boot(get_absolute_time());
    while (to_ms_since_boot(get_absolute_time()) - start_time < DISPLAY_TIME * 1000) {
        printf("MIN");
        for (int i = 0; i < NUM_SENSORS; i++) {
            printf(",%d", min_vals[i]);
        }
        printf("\n");
        sleep_ms(SAMPLE_DELAY_MS);
    }
    
    printf("COLOCAR EN SUPERFICIE NEGRA - CAPTURANDO MAXIMOS\n");
    sleep_ms(5000);

    for (int i = 0; i < NUM_SENSORS; i++) {
        max_vals[i] = 0;
    }
    
    for (int sample = 0; sample < NUM_SAMPLES; sample++) {
        read_all_sensors(values);
        for (int i = 0; i < NUM_SENSORS; i++) {
            max_vals[i] += values[i];
        }
        sleep_ms(100);
    }
    
    for (int i = 0; i < NUM_SENSORS; i++) {
        max_vals[i] /= NUM_SAMPLES;
    }

    start_time = to_ms_since_boot(get_absolute_time());
    while (to_ms_since_boot(get_absolute_time()) - start_time < DISPLAY_TIME * 1000) {
        printf("MAX");
        for (int i = 0; i < NUM_SENSORS; i++) {
            printf(",%d", max_vals[i]);
        }
        printf("\n");
        sleep_ms(SAMPLE_DELAY_MS);
    }
    
    calibrated = true;
}

void activity3() {
    uint16_t values[NUM_SENSORS];
    uint16_t cal_vals[NUM_SENSORS];
    uint32_t start_time;
    
    printf("COLOCAR EN SUPERFICIE NEGRA - VALORES CALIBRADOS\n");
    sleep_ms(5000);
    
    start_time = to_ms_since_boot(get_absolute_time());
    while (to_ms_since_boot(get_absolute_time()) - start_time < DISPLAY_TIME * 1000) {
        read_all_sensors(values);
        
        printf("CAL");
        for (int i = 0; i < NUM_SENSORS; i++) {
            cal_vals[i] = calibrate_value(values[i], i);
            printf(",%d", cal_vals[i]);
        }
        printf("\n");
        
        sleep_ms(SAMPLE_DELAY_MS);
    }
    
    printf("COLOCAR EN SUPERFICIE BLANCA - VALORES CALIBRADOS\n");
    sleep_ms(5000);
    
    start_time = to_ms_since_boot(get_absolute_time());
    while (to_ms_since_boot(get_absolute_time()) - start_time < DISPLAY_TIME * 1000) {
        read_all_sensors(values);
        
        printf("CAL");
        for (int i = 0; i < NUM_SENSORS; i++) {
            cal_vals[i] = calibrate_value(values[i], i);
            printf(",%d", cal_vals[i]);
        }
        printf("\n");
        
        sleep_ms(SAMPLE_DELAY_MS);
    }
}

float calculate_position(uint16_t *cal_vals) {
    float total_weight = 0.0f;
    float total_value = 0.0f;
    
    for (int i = 0; i < NUM_SENSORS; i++) {
        total_weight += (float)cal_vals[i];
        total_value += (float)cal_vals[i] * sensor_positions[i];
    }

    if (total_weight < 500.0f) { 
        if (last_position < 0.0f) {
            return -45.0f;
        } else {
            return 45.0f;
        }
    } else {
        float position = total_value / total_weight;
        last_position = position;
        return position;
    }
}

void activity4() {
    uint16_t values[NUM_SENSORS];
    uint16_t cal_vals[NUM_SENSORS];
    
    printf("INICIANDO SEGUIMIENTO EN TIEMPO REAL\n");
    
    while (true) {
        read_all_sensors(values);

        for (int i = 0; i < NUM_SENSORS; i++) {
            cal_vals[i] = calibrate_value(values[i], i);
        }

        float position = calculate_position(cal_vals);

        printf("CAL");
        for (int i = 0; i < NUM_SENSORS; i++) {
            printf(",%d", cal_vals[i]);
        }
        printf("\n");

        printf("POS,%.3f\n", position);
        
        sleep_ms(SAMPLE_DELAY_MS);
    }
}

void init_system() {
    stdio_init_all();
    
    gpio_init(LED_ON);
    gpio_set_dir(LED_ON, GPIO_OUT);
    gpio_init(C0);
    gpio_set_dir(C0, GPIO_OUT);
    gpio_init(C1);
    gpio_set_dir(C1, GPIO_OUT);
    gpio_init(C2);
    gpio_set_dir(C2, GPIO_OUT);
    gpio_init(C3);
    gpio_set_dir(C3, GPIO_OUT);
    
    adc_init();
    adc_gpio_init(ANALOG_PIN);
    adc_select_input(0);
    
    gpio_put(LED_ON, 1);
    
    printf("SISTEMA INICIALIZADO - SEGUIDOR DE LINEA\n");
    printf("VALORES CALIBRADOS EN RANGO 0-4095\n");
}

int main() {
    init_system();
    sleep_ms(2000);
    
    activity1();
    activity2();
    activity3();
    activity4();
    
    return 0;
}