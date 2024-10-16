<script setup>
import {ref} from 'vue'
import qs from 'qs'
import requestUtil from '@/utils/request'
import image_robot from '@/assets/robot.png';
import image_customer_service from '@/assets/customer_service.png'

const info = ref({
  "type": "",
  "price": "",
  "transportation": "",
  "temp": "",
  "air": "",
  "message": ""
})

const reply = ref({
  "message": ""
})

const city = ref({
  "option1": "",
  "option2": "",
  "option3": "",
  "option4": "",
  "option5": "",
  "description1": "",
  "description2": "",
  "description3": "",
  "description4": "",
  "description5": "",
})

const typeOptions = [
  {
    value: 'Humanities',
    label: 'A city with a rich historical heritage.',
  },
  {
    value: 'Nature',
    label: 'A resort city with natural scenery.',
  },
  {
    value: 'Balanced',
    label: 'A comprehensive city with various aspects.',
  },
]

const priceOptions = [
  {
    value: 'Expensive',
    label: 'A city with high costs.',
  },
  {
    value: 'Medium',
    label: 'A city with moderate costs.',
  },
  {
    value: 'Cheap',
    label: 'A city with low costs.',
  },
  {
    value: 'Expensive Medium Cheap',
    label: 'All are acceptable.',
  },
]

const transportationOptions = [
  {
    value: 'Good',
    label: 'Yes, a city with good transportation is essential.',
  },
  {
    value: 'Good Medium Bad',
    label: 'All are acceptable.',
  },
]

const tempOptions = [
  {
    value: 'Cold',
    label: 'A relatively cold city.',
  },
  {
    value: 'Temper',
    label: 'A city with moderate temperature.',
  },
  {
    value: 'Warm',
    label: 'A relatively warm city.',
  },
  {
    value: 'Cold Temper Warm',
    label: 'All are acceptable.',
  },
]

const airOptions = [
  {
    value: 'Good',
    label: 'Yes, a city with high air quality is necessary.',
  },
  {
    value: 'Medium Bad Unknown',
    label: 'All are acceptable.',
  },
]

// send the user's selection as the information of the city
const informationSubmit = async () => {
  let result = await requestUtil.post("recommendation/information?" + qs.stringify(info.value))
  let data = result.data
  if (data.code == 200) {
    console.log("test message" + data.info)
  } else {
    console.log("fail to submit information")
  }
}

// send the user's message to the robot and get the reply
const messageSend = async () => {
  let result = await requestUtil.get("recommendation/message?" + qs.stringify(info.value))
  let data = result.data
  if (data.code == 200) {
    reply.value.message = data.message
    info.value.message = ""
    console.log(reply.value.message)
  } else {
    console.log("fail to send message")
  }
}

// get the recommended cities
const getOutput = async () => {
  city.value.option1 = ""
  city.value.option2 = ""
  city.value.option3 = ""
  city.value.option4 = ""
  city.value.option5 = ""
  city.value.description1 = ""
  city.value.description2 = ""
  city.value.description3 = ""
  city.value.description4 = ""
  city.value.description5 = ""
  let result = await requestUtil.get("recommendation/city")
  let data = result.data
  if (data.code == 200) {
    city.value = JSON.parse(data.city)
  } else {
    console.log("fail to get output")
  }
}

</script>

<template>
  <div class="common-layout">
    <el-container class="container_1">
      <el-header class="title_intro">
        <!--title-->
        <el-form>
          <el-text class="title">Welcome to Travel Recommendation!</el-text>
        </el-form>
        <!--introduction-->
        <el-form>
          <el-text class="intro">Help find your ideal travel destination</el-text>
        </el-form>
      </el-header>
      <el-form class="background_colour">
        <el-container class="container_2">
          <el-container>
            <el-main>
              <!--text:select options-->
              <el-form>
                <el-text class="text_general">Please select your preference:</el-text>
              </el-form>
              <!--selections-->
              <el-form class="select">
                <el-text class="text_select">What type of city do you want to travel to?</el-text>
                <el-select v-model="info.type" class="box_select" placeholder="Select" size="large">
                  <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value"/>
                </el-select>
              </el-form>
              <el-form class="select">
                <el-text class="text_select">What are your requirements for the consumption level in a city?</el-text>
                <el-select v-model="info.price" class="box_select" placeholder="Select" size="large">
                  <el-option v-for="item in priceOptions" :key="item.value" :label="item.label" :value="item.value"/>
                </el-select>
              </el-form>
              <el-form class="select">
                <el-text class="text_select">Do you have high requirements for the transportation in city?
                </el-text>
                <el-select v-model="info.transportation" class="box_select" placeholder="Select" size="large">
                  <el-option v-for="item in transportationOptions" :key="item.value" :label="item.label"
                             :value="item.value"/>
                </el-select>
              </el-form>
              <el-form class="select">
                <el-text class="text_select">What is your expectation for the temperature in cities?</el-text>
                <el-select v-model="info.temp" class="box_select" placeholder="Select" size="large">
                  <el-option v-for="item in tempOptions" :key="item.value" :label="item.label" :value="item.value"/>
                </el-select>
              </el-form>
              <el-form class="select">
                <el-text class="text_select">Do you have high requirements for air quality in city?</el-text>
                <el-select v-model="info.air" class="box_select" placeholder="Select" size="large">
                  <el-option v-for="item in airOptions" :key="item.value" :label="item.label"
                             :value="item.value"/>
                </el-select>
              </el-form>
              <!--confirm the information-->
              <el-form class="button_confirm">
                <el-button type="primary" @click="informationSubmit">Confirm</el-button>
              </el-form>
            </el-main>
          </el-container>
          <el-container class="container_3">
            <!--chat robot-->
            <el-form class="bot">
              <!--reply from the robot-->
              <el-form class="reply_bot">
                <el-text v-if="!reply.message" class="text_bot">My name is CHATTY. Please tell me more detailed
                  requirements through text input!
                </el-text>
                <el-text v-if="reply.message" class="text_bot">{{ reply.message }}</el-text>
              </el-form>
              <!--pic of robot-->
              <el-form>
                <el-image class="img_robot" :src="image_customer_service"/>
              </el-form>
            </el-form>
            <!--message from the user-->
            <el-form class="msg_user">
              <el-input v-model="info.message" :rows="3" type="textarea"
                        placeholder="Please tell the bot what you want">
                {{ info.message }}
              </el-input>
            </el-form>
            <!--send message to the robot-->
            <el-form class="button_send">
              <el-button type="primary" @click="messageSend">Send</el-button>
            </el-form>
          </el-container>
        </el-container>
        <!--search for cities-->
        <el-form>
          <el-button type="primary" @click="getOutput">Search for city</el-button>
        </el-form>
        <el-form class="recommendation">
          <el-text v-if="city.option1 || city.option2 || city.option3 || city.option4 || city.option5"
                   class="text_recommend">We recommend these cities for you!
          </el-text>
        </el-form>
        <el-form class="recommendation">
          <el-text class="cities" v-if="city.option1">{{ city.option1 }}</el-text>
          <el-text class="text_describe" v-if="city.option1">{{ city.description1 }}</el-text>
          <el-text class="cities" v-if="city.option2">{{ city.option2 }}</el-text>
          <el-text class="text_describe" v-if="city.option2">{{ city.description2 }}</el-text>
          <el-text class="cities" v-if="city.option3">{{ city.option3 }}</el-text>
          <el-text class="text_describe" v-if="city.option3">{{ city.description3 }}</el-text>
          <el-text class="cities" v-if="city.option4">{{ city.option4 }}</el-text>
          <el-text class="text_describe" v-if="city.option4">{{ city.description4 }}</el-text>
          <el-text class="cities" v-if="city.option5">{{ city.option5 }}</el-text>
          <el-text class="text_describe" v-if="city.option5">{{ city.description5 }}</el-text>
        </el-form>
      </el-form>
      <el-footer class="designer">Designed by Team RushB -- NUS-ISS-GROUP 1</el-footer>
    </el-container>
  </div>
</template>

<style scoped>

.background_colour {
  background-color: rgba(255, 255, 255, 0.8);
  padding: 50px;
  border-radius: 10px;
  color: black;
}

.container_1 {
  padding-right: 60px;
  padding-left: 60px;
}

.container_2 {
  padding-top: 50px;
}

.container_3 {
  padding-top: 25px;
  width: 600px;
  display: flex;
  flex-direction: column;
}

.title_intro {
  padding-bottom: 100px;
}

.title {
  font-family: 'Arial Black';
  font-size: 35px;
}

.intro {
  font-size: 20px;
}

.text_general {
  font-size: 20px;
}

.bot {
  padding-top: 20px;
  display: flex;
}

.reply_bot {
  padding-top: 50px;
  width: 300px;
}

.text_bot {
  font-size: 20px;
  align-items: center;
}

.img_robot {
  padding-left: 20px;
  width: 200px;
  height: 200px;
}

.msg_user {
  padding-top: 20px;
}

.select {
  display: flex;
  padding-top: 20px;
}

.text_select {
  width: 500px;
  text-align: left;
}

.box_select {
  width: 300px;
  text-align: right;
}

.button_confirm {
  padding-top: 20px;
}

.button_send {
  padding-top: 20px;
}

.recommendation {
  padding-top: 60px;
  display: flex;
  flex-direction: column;
}

.text_recommend {
  font-size: 30px;
}

.text_describe {
  text-align: left;
}

.cities {
  padding: 20px;
  font-size: 30px;
  font-family: 'Arial Black';
}

.designer {
  padding-top: 100px;
}

</style>