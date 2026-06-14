/*
 * Minimal GPIO blink for FRDM-MCXA266.
 *
 * Toggles the on-board blue LED (P3_21 / GPIO3[21]) once per second. The pin
 * mux and clock setup come from the MCUXpresso Config Tools output in board/
 * (see the README "Project layout" section).
 */
#include "fsl_common.h"
#include "fsl_gpio.h"

#include "clock_config.h"
#include "pin_mux.h"

int main()
{
    // Clocks (and the core LDO / SRAM voltage via SPC) and the LED pin.
    BOARD_InitBootClocks();
    BOARD_InitLEDsPins();

    while (true)
    {
        GPIO_PortToggle(BOARD_INITLEDSPINS_LED_BLUE_GPIO,
                        BOARD_INITLEDSPINS_LED_BLUE_GPIO_PIN_MASK);
        SDK_DelayAtLeastUs(500000U, SystemCoreClock);
    }
}
