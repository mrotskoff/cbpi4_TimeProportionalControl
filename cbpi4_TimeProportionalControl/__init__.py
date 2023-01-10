
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
import asyncio
from cbpi.api import *

@parameters([Property.Number(label = "Sample_Period", configurable = True, default_value = 30, description="Time period in seconds during which each on-time/off-time cycle is proportioned"),
             Property.Number(label = "Proportional_Band", configurable = True, default_value = 10, description="Degrees below target temp that will result in 100% heater on-time for the sample period.  Above this temp, heater will be proportioned.")])

class TimeProportionalControl(CBPiKettleLogic):

    async def on_stop(self):
        await self.actor_off(self.heater)
        pass

    async def run(self):
        try:
            self.TEMP_UNIT = self.get_config_value("TEMP_UNIT", "C")
            sample_period = int(self.props.get("Sample_Period", 30))
            proportional_band = int(self.props.get("Proportional_Band", 10))
            self.kettle = self.get_kettle(self.id)
            self.heater = self.kettle.heater
            self.heater_actor = self.cbpi.actor.find_by_id(self.heater)
                       
            while self.running == True:
                self._logger.debug('---entering TimeProportionalControl run loop---')

                current_temp = self.get_sensor_value(self.kettle.sensor).get("value")
                target_temp = self.get_kettle_target_temp(self.id)

                self._logger.debug('current temp: {0}'.format(current_temp))
                self._logger.debug('target_temp: {0}'.format(target_temp))
            
                (on_time, off_time) = calculate_on_off_time(current_temp, target_temp, proportional_band, sample_period)        
                self._logger.debug('on_time: {0}'.format(on_time))
                self._logger.debug('off_time: {0}'.format(off_time))
            
                if on_time > 0:
                    self._logger.debug('turning heater on for {0} seconds'.format(on_time))
                    await self.actor_on(self.heater)
                    await asyncio.sleep(on_time)
                
                if off_time > 0:
                    self._logger.debug('turning heater off for {0} seconds'.format(off_time))
                    await self.actor_off(self.heater)
                    await asyncio.sleep(off_time)
                
                self._logger.debug('---exiting TimeProportionalControl run loop ---')
            
        except asyncio.CancelledError as e:
            pass
        except Exception as e:
            self._logger.error("TimeProportionalControl Error {}".format(e))
        finally:
            self.running = False
            await self.actor_off(self.heater)

def calculate_on_off_time(current_temp, target_temp, proportional_band, sample_period):
    on_time = 0

    if target_temp - current_temp > proportional_band:
        on_time = sample_period
    elif current_temp >= target_temp:
        on_time = 0
    else:
        on_time = ((target_temp - current_temp) / proportional_band) * sample_period
            
    off_time = sample_period - on_time

    return (on_time, off_time)

def setup(cbpi):
    cbpi.plugin.register("TimeProportionalControl", TimeProportionalControl)

# quick test
'''
target = 100
period = 60
band = 20
for i in range(50, 120):
    (on_time, off_time) = calculate_on_off_time(i, target, band, period)
    print("current temp: {}".format(i))
    print("on_time {}".format(on_time))
    print("off_time {}".format(off_time))
'''