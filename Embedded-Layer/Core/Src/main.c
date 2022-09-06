/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2022 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "usb_host.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "string.h"
#include "stdio.h"
#include <stdbool.h>
#include "icm20648.h"
#include "math.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

#define DEVADDRESS (208)
#define pi 3.14159
#define UVReadAddress 0xA7
#define UVWriteAddress 0xA6
#define N (6)
#define numSamples (20)
#define sampleFreq (40)
#define Accel_Indicator (0)
#define Angular_Indicator (1)

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
CRC_HandleTypeDef hcrc;

DMA2D_HandleTypeDef hdma2d;

I2C_HandleTypeDef hi2c3;

LTDC_HandleTypeDef hltdc;

SPI_HandleTypeDef hspi5;

TIM_HandleTypeDef htim1;

UART_HandleTypeDef huart1;
UART_HandleTypeDef huart2;

SDRAM_HandleTypeDef hsdram1;

/* USER CODE BEGIN PV */
int lights = 1;
uint8_t counter = 0;
float threshold = 1.8;
int flag = 0;
int flag2 = 0;
int sampled = 0;
int uvsampled = 0;
uint8_t uvaddress = 0x53 <<1 ;
char strbuf[256];
float GyroCovariance[N][N];
float AccNoise[3][3];
float AngNoise[3][3];
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_CRC_Init(void);
static void MX_DMA2D_Init(void);
static void MX_FMC_Init(void);
static void MX_I2C3_Init(void);
static void MX_LTDC_Init(void);
static void MX_SPI5_Init(void);
static void MX_TIM1_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_USART2_UART_Init(void);
void MX_USB_HOST_Process(void);

/* USER CODE BEGIN PFP */
void GyroInit(float *accelbias, float *gyrobias);
void UVInit(void);
void SampleCovariance(float GyroCovariance[6][6]);
void PrintGyroCovariance(char * strbuf,float GyroCovariance[6][6]);
void PrintGyro(void);
void PrintUV(void);
void PrintString(char * strbuf);
void GetGyroData(float * tempreading,float * acceleration, float * angular_velocity, uint32_t * time,int print);
void GetUVData(uint8_t * rawuv,uint32_t * time);
void SampleNoise(float AccNoise[3][3], float AngNoise[3][3]);
void PrintNoise(char * strbuf,float Noise[3][3],int indicator);
float norm(float * vect);
/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */


  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_CRC_Init();
  MX_DMA2D_Init();
  MX_FMC_Init();
  MX_I2C3_Init();
  MX_LTDC_Init();
  MX_SPI5_Init();
  MX_TIM1_Init();
  MX_USART1_UART_Init();
  MX_USB_HOST_Init();
  MX_USART2_UART_Init();
  /* USER CODE BEGIN 2 */
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */

  // Initialize calibration variables

  float accelbias[3];
  float gyrobias[3];

  // Initialize data buffers

  float tempreading;
  float acceleration[3];
  float angular_velocity[3];
  uint8_t rawuv[3];
  uint32_t time = 0;

  // Call initializing procedure

  GyroInit(accelbias,gyrobias);
  UVInit();

  HAL_Delay(200);

  sprintf(strbuf,"S 1,1,1\r\n");
  PrintString(strbuf);

  HAL_Delay(1000);

  SampleCovariance(GyroCovariance);
  PrintGyroCovariance(strbuf, GyroCovariance);

  sprintf(strbuf,"T Please move sensor to rest position for environment noise calibration\r\n");
  PrintString(strbuf);

  HAL_Delay(2000);

//  PrintString('T Calibration will now begin\r\n');

  SampleNoise(AccNoise, AngNoise);
  PrintNoise(strbuf,AccNoise,Accel_Indicator);
  PrintNoise(strbuf,AngNoise,Angular_Indicator);

  HAL_Delay(200);

  sprintf(strbuf,"C 1,1,1\r\n");
  PrintString(strbuf);

  sprintf(strbuf,"T Calibration is now complete, data transmission will begin.\r\n");
  PrintString(strbuf);

  HAL_Delay(500);

  while (1)
  {

	  // Flag set in pin change interrupt PA3 - used for gyro reading

	  if (sampled == 1)
	  {

	  GetGyroData(&tempreading,acceleration,angular_velocity,&time,1);

//	  GetUVData(rawuv,&time);

	  sampled = 0;

	  // Flag set in pin change interrupt PA10 - used for UV reading (but it doesn't work due to the
	  // manufacturer, so we just sampled with the gyroscope for the UV sensor

	  if (uvsampled == 1)
	  {

		  GetUVData(rawuv,&time);

		  uvsampled = 0;
	  }

      }


    /* USER CODE END WHILE */
    MX_USB_HOST_Process();

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE3);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 4;
  RCC_OscInitStruct.PLL.PLLN = 72;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 3;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV2;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_2) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief CRC Initialization Function
  * @param None
  * @retval None
  */
static void MX_CRC_Init(void)
{

  /* USER CODE BEGIN CRC_Init 0 */

  /* USER CODE END CRC_Init 0 */

  /* USER CODE BEGIN CRC_Init 1 */

  /* USER CODE END CRC_Init 1 */
  hcrc.Instance = CRC;
  if (HAL_CRC_Init(&hcrc) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN CRC_Init 2 */

  /* USER CODE END CRC_Init 2 */

}

/**
  * @brief DMA2D Initialization Function
  * @param None
  * @retval None
  */
static void MX_DMA2D_Init(void)
{

  /* USER CODE BEGIN DMA2D_Init 0 */

  /* USER CODE END DMA2D_Init 0 */

  /* USER CODE BEGIN DMA2D_Init 1 */

  /* USER CODE END DMA2D_Init 1 */
  hdma2d.Instance = DMA2D;
  hdma2d.Init.Mode = DMA2D_M2M;
  hdma2d.Init.ColorMode = DMA2D_OUTPUT_ARGB8888;
  hdma2d.Init.OutputOffset = 0;
  hdma2d.LayerCfg[1].InputOffset = 0;
  hdma2d.LayerCfg[1].InputColorMode = DMA2D_INPUT_ARGB8888;
  hdma2d.LayerCfg[1].AlphaMode = DMA2D_NO_MODIF_ALPHA;
  hdma2d.LayerCfg[1].InputAlpha = 0;
  if (HAL_DMA2D_Init(&hdma2d) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_DMA2D_ConfigLayer(&hdma2d, 1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN DMA2D_Init 2 */

  /* USER CODE END DMA2D_Init 2 */

}

/**
  * @brief I2C3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C3_Init(void)
{

  /* USER CODE BEGIN I2C3_Init 0 */

  /* USER CODE END I2C3_Init 0 */

  /* USER CODE BEGIN I2C3_Init 1 */

  /* USER CODE END I2C3_Init 1 */
  hi2c3.Instance = I2C3;
  hi2c3.Init.ClockSpeed = 100000;
  hi2c3.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c3.Init.OwnAddress1 = 0;
  hi2c3.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c3.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c3.Init.OwnAddress2 = 0;
  hi2c3.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c3.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c3) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Analogue filter
  */
  if (HAL_I2CEx_ConfigAnalogFilter(&hi2c3, I2C_ANALOGFILTER_ENABLE) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Digital filter
  */
  if (HAL_I2CEx_ConfigDigitalFilter(&hi2c3, 0) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C3_Init 2 */

  /* USER CODE END I2C3_Init 2 */

}

/**
  * @brief LTDC Initialization Function
  * @param None
  * @retval None
  */
static void MX_LTDC_Init(void)
{

  /* USER CODE BEGIN LTDC_Init 0 */

  /* USER CODE END LTDC_Init 0 */

  LTDC_LayerCfgTypeDef pLayerCfg = {0};
  LTDC_LayerCfgTypeDef pLayerCfg1 = {0};

  /* USER CODE BEGIN LTDC_Init 1 */

  /* USER CODE END LTDC_Init 1 */
  hltdc.Instance = LTDC;
  hltdc.Init.HSPolarity = LTDC_HSPOLARITY_AL;
  hltdc.Init.VSPolarity = LTDC_VSPOLARITY_AL;
  hltdc.Init.DEPolarity = LTDC_DEPOLARITY_AL;
  hltdc.Init.PCPolarity = LTDC_PCPOLARITY_IPC;
  hltdc.Init.HorizontalSync = 7;
  hltdc.Init.VerticalSync = 3;
  hltdc.Init.AccumulatedHBP = 14;
  hltdc.Init.AccumulatedVBP = 5;
  hltdc.Init.AccumulatedActiveW = 654;
  hltdc.Init.AccumulatedActiveH = 485;
  hltdc.Init.TotalWidth = 660;
  hltdc.Init.TotalHeigh = 487;
  hltdc.Init.Backcolor.Blue = 0;
  hltdc.Init.Backcolor.Green = 0;
  hltdc.Init.Backcolor.Red = 0;
  if (HAL_LTDC_Init(&hltdc) != HAL_OK)
  {
    Error_Handler();
  }
  pLayerCfg.WindowX0 = 0;
  pLayerCfg.WindowX1 = 0;
  pLayerCfg.WindowY0 = 0;
  pLayerCfg.WindowY1 = 0;
  pLayerCfg.PixelFormat = LTDC_PIXEL_FORMAT_ARGB8888;
  pLayerCfg.Alpha = 0;
  pLayerCfg.Alpha0 = 0;
  pLayerCfg.BlendingFactor1 = LTDC_BLENDING_FACTOR1_CA;
  pLayerCfg.BlendingFactor2 = LTDC_BLENDING_FACTOR2_CA;
  pLayerCfg.FBStartAdress = 0;
  pLayerCfg.ImageWidth = 0;
  pLayerCfg.ImageHeight = 0;
  pLayerCfg.Backcolor.Blue = 0;
  pLayerCfg.Backcolor.Green = 0;
  pLayerCfg.Backcolor.Red = 0;
  if (HAL_LTDC_ConfigLayer(&hltdc, &pLayerCfg, 0) != HAL_OK)
  {
    Error_Handler();
  }
  pLayerCfg1.WindowX0 = 0;
  pLayerCfg1.WindowX1 = 0;
  pLayerCfg1.WindowY0 = 0;
  pLayerCfg1.WindowY1 = 0;
  pLayerCfg1.PixelFormat = LTDC_PIXEL_FORMAT_ARGB8888;
  pLayerCfg1.Alpha = 0;
  pLayerCfg1.Alpha0 = 0;
  pLayerCfg1.BlendingFactor1 = LTDC_BLENDING_FACTOR1_CA;
  pLayerCfg1.BlendingFactor2 = LTDC_BLENDING_FACTOR2_CA;
  pLayerCfg1.FBStartAdress = 0;
  pLayerCfg1.ImageWidth = 0;
  pLayerCfg1.ImageHeight = 0;
  pLayerCfg1.Backcolor.Blue = 0;
  pLayerCfg1.Backcolor.Green = 0;
  pLayerCfg1.Backcolor.Red = 0;
  if (HAL_LTDC_ConfigLayer(&hltdc, &pLayerCfg1, 1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN LTDC_Init 2 */

  /* USER CODE END LTDC_Init 2 */

}

/**
  * @brief SPI5 Initialization Function
  * @param None
  * @retval None
  */
static void MX_SPI5_Init(void)
{

  /* USER CODE BEGIN SPI5_Init 0 */

  /* USER CODE END SPI5_Init 0 */

  /* USER CODE BEGIN SPI5_Init 1 */

  /* USER CODE END SPI5_Init 1 */
  /* SPI5 parameter configuration*/
  hspi5.Instance = SPI5;
  hspi5.Init.Mode = SPI_MODE_MASTER;
  hspi5.Init.Direction = SPI_DIRECTION_2LINES;
  hspi5.Init.DataSize = SPI_DATASIZE_8BIT;
  hspi5.Init.CLKPolarity = SPI_POLARITY_LOW;
  hspi5.Init.CLKPhase = SPI_PHASE_1EDGE;
  hspi5.Init.NSS = SPI_NSS_SOFT;
  hspi5.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_16;
  hspi5.Init.FirstBit = SPI_FIRSTBIT_MSB;
  hspi5.Init.TIMode = SPI_TIMODE_DISABLE;
  hspi5.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
  hspi5.Init.CRCPolynomial = 10;
  if (HAL_SPI_Init(&hspi5) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN SPI5_Init 2 */

  /* USER CODE END SPI5_Init 2 */

}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 0;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 65535;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim1, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/* FMC initialization function */
static void MX_FMC_Init(void)
{

  /* USER CODE BEGIN FMC_Init 0 */

  /* USER CODE END FMC_Init 0 */

  FMC_SDRAM_TimingTypeDef SdramTiming = {0};

  /* USER CODE BEGIN FMC_Init 1 */

  /* USER CODE END FMC_Init 1 */

  /** Perform the SDRAM1 memory initialization sequence
  */
  hsdram1.Instance = FMC_SDRAM_DEVICE;
  /* hsdram1.Init */
  hsdram1.Init.SDBank = FMC_SDRAM_BANK2;
  hsdram1.Init.ColumnBitsNumber = FMC_SDRAM_COLUMN_BITS_NUM_8;
  hsdram1.Init.RowBitsNumber = FMC_SDRAM_ROW_BITS_NUM_12;
  hsdram1.Init.MemoryDataWidth = FMC_SDRAM_MEM_BUS_WIDTH_16;
  hsdram1.Init.InternalBankNumber = FMC_SDRAM_INTERN_BANKS_NUM_4;
  hsdram1.Init.CASLatency = FMC_SDRAM_CAS_LATENCY_3;
  hsdram1.Init.WriteProtection = FMC_SDRAM_WRITE_PROTECTION_DISABLE;
  hsdram1.Init.SDClockPeriod = FMC_SDRAM_CLOCK_PERIOD_2;
  hsdram1.Init.ReadBurst = FMC_SDRAM_RBURST_DISABLE;
  hsdram1.Init.ReadPipeDelay = FMC_SDRAM_RPIPE_DELAY_1;
  /* SdramTiming */
  SdramTiming.LoadToActiveDelay = 2;
  SdramTiming.ExitSelfRefreshDelay = 7;
  SdramTiming.SelfRefreshTime = 4;
  SdramTiming.RowCycleDelay = 7;
  SdramTiming.WriteRecoveryTime = 3;
  SdramTiming.RPDelay = 2;
  SdramTiming.RCDDelay = 2;

  if (HAL_SDRAM_Init(&hsdram1, &SdramTiming) != HAL_OK)
  {
    Error_Handler( );
  }

  /* USER CODE BEGIN FMC_Init 2 */

  /* USER CODE END FMC_Init 2 */
}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOF_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();
  __HAL_RCC_GPIOG_CLK_ENABLE();
  __HAL_RCC_GPIOE_CLK_ENABLE();
  __HAL_RCC_GPIOD_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOC, NCS_MEMS_SPI_Pin|CSX_Pin|OTG_FS_PSO_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(ACP_RST_GPIO_Port, ACP_RST_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOD, RDX_Pin|WRX_DCX_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOG, LD3_Pin|LD4_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin : PC13 */
  GPIO_InitStruct.Pin = GPIO_PIN_13;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
  GPIO_InitStruct.Pull = GPIO_PULLUP;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pins : NCS_MEMS_SPI_Pin CSX_Pin OTG_FS_PSO_Pin */
  GPIO_InitStruct.Pin = NCS_MEMS_SPI_Pin|CSX_Pin|OTG_FS_PSO_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pins : B1_Pin MEMS_INT1_Pin MEMS_INT2_Pin TP_INT1_Pin */
  GPIO_InitStruct.Pin = B1_Pin|MEMS_INT1_Pin|MEMS_INT2_Pin|TP_INT1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_EVT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

  /*Configure GPIO pin : ACP_RST_Pin */
  GPIO_InitStruct.Pin = ACP_RST_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(ACP_RST_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : OTG_FS_OC_Pin */
  GPIO_InitStruct.Pin = OTG_FS_OC_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_EVT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(OTG_FS_OC_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : BOOT1_Pin */
  GPIO_InitStruct.Pin = BOOT1_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(BOOT1_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pin : TE_Pin */
  GPIO_InitStruct.Pin = TE_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(TE_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : RDX_Pin WRX_DCX_Pin */
  GPIO_InitStruct.Pin = RDX_Pin|WRX_DCX_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);

  /*Configure GPIO pins : LD3_Pin LD4_Pin */
  GPIO_InitStruct.Pin = LD3_Pin|LD4_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);

}

/* USER CODE BEGIN 4 */

void GyroInit(float *accelbias, float *gyrobias)
{
	ICM20648_init(&hi2c3);

	ICM20648_accelGyroCalibrate(accelbias,gyrobias);
	ICM20648_sensorEnable(true,true,true);

	ICM20648_gyroSampleRateSet(sampleFreq);
	ICM20648_accelSampleRateSet(sampleFreq);

	ICM20648_accelFullscaleSet(ICM20648_ACCEL_FULLSCALE_16G);
	ICM20648_gyroFullscaleSet(ICM20648_GYRO_FULLSCALE_2000DPS);

	ICM20648_registerWrite(17,1);

	ICM20648_bankSelect(0);
}

void PrintGyro(void)
{
	int currentaddress;
	int bank;

	uint8_t readbuf[1];

	for (bank = 0;bank<4;bank++)
	{
	ICM20648_bankSelect(bank);
	for (currentaddress = 0;currentaddress <128;currentaddress++)
	  	{
	  	HAL_I2C_Mem_Read(&hi2c3,DEVADDRESS,(uint16_t)currentaddress,(uint16_t)1,readbuf,1,HAL_MAX_DELAY);
	  	sprintf(strbuf, "Register (Gyro) : %3d, Bank %d, Contents : %2x\r\n",currentaddress,bank,readbuf[0]);
	  	PrintString(strbuf);
	  	}
	}
}

void UVInit(void)
{
      uint8_t buf[1];

  	  //Initialize by turning on UV sensor to active and enabling interrupt

      buf[0] = 0b00001010;
      HAL_I2C_Mem_Write(&hi2c3,UVWriteAddress,(uint16_t)0x00,(uint16_t)1,buf,1,HAL_MAX_DELAY);


      buf[0] = 0b00110100;
  	  HAL_I2C_Mem_Write(&hi2c3,UVWriteAddress,(uint16_t)0x19,(uint16_t)1,buf,1,HAL_MAX_DELAY);

  	  //Set resolution and sample collection time

  	  buf[0] = 0b00000111;
      HAL_I2C_Mem_Write(&hi2c3,UVWriteAddress,(uint16_t)0x04,(uint16_t)1,buf,1,HAL_MAX_DELAY);

	  //Set gain

	  buf[0] = 0b00000001;
	  HAL_I2C_Mem_Write(&hi2c3,UVWriteAddress,(uint16_t)0x04,(uint16_t)1,buf,1,HAL_MAX_DELAY);
}

void PrintUV(void)
{
	int currentaddress;
	uint8_t readbuf[1];
	for (currentaddress = 0;currentaddress <0x26;currentaddress++)
		{
		HAL_I2C_Mem_Read(&hi2c3,UVReadAddress,(uint16_t)currentaddress,(uint16_t)1,readbuf,1,HAL_MAX_DELAY);
		sprintf(strbuf, "Register (UV) : %d, Contents : %x\r\n",currentaddress,readbuf[0]);
		PrintString(strbuf);
		}
}

void PrintString(char * strbuf)
{
	int len = strlen(strbuf);
	HAL_UART_Transmit(&huart1,(uint8_t*)strbuf,len,HAL_MAX_DELAY);
}

void GetGyroData(float * tempreading,float * acceleration, float * angular_velocity, uint32_t * time,int print)
{
	ICM20648_isDataReady();
	ICM20648_temperatureRead(tempreading);
	ICM20648_accelDataRead(acceleration);
	ICM20648_gyroDataRead(angular_velocity);
	*time = HAL_GetTick();

	// Data printed in format: time,temp,(ax,ay,az),(wx,wy,wz), ||acceleration||, ||angular velocity||

	float normvel = norm(acceleration);
	float normangular = norm(angular_velocity);

	if (print == 1)
	{
	sprintf(strbuf,"G %8lu,%7.3f,%8.3f,%8.3f,%8.3f,%7.3f,%7.3f,%7.3f,%8.3f,%7.3f\r\n",
		*time,
		*tempreading,
		acceleration[0],acceleration[1],acceleration[2],
		angular_velocity[0],angular_velocity[1],angular_velocity[2],
		normvel,normangular);
	PrintString(strbuf);
	}
}

void GetUVData(uint8_t * rawuv,uint32_t * time)
{
	uint32_t val;
	float uvout;

	// Read from 3 registers as specified in datasheet

	HAL_I2C_Mem_Read(&hi2c3,UVReadAddress,(uint32_t)0x10,(uint32_t)1,rawuv,1,HAL_MAX_DELAY);
	HAL_I2C_Mem_Read(&hi2c3,UVReadAddress,(uint32_t)0x11,(uint32_t)1,rawuv+1,1,HAL_MAX_DELAY);
	HAL_I2C_Mem_Read(&hi2c3,UVReadAddress,(uint32_t)0x12,(uint32_t)1,rawuv+2,1,HAL_MAX_DELAY);

	// Combine the data

	val = ((uint32_t)rawuv[2]<<16 | rawuv[1]<<8 | rawuv[0]);

	// Use the formula given in datasheet to convert to UV index
	uvout = (float)val/2300.0;

	// Data printed in format: time, UV index

	sprintf(strbuf, "%8lu,%12.3f\r\n\r\n",*time,uvout);
	PrintString(strbuf);
}

void SampleNoise(float AccNoise[3][3], float AngNoise[3][3])
{
	int samplecount = 0;
	float x[N][numSamples];
	float xbar[N];

	while (samplecount < numSamples)
	{
		if (samplecount < numSamples)
		{
			if (sampled == 1)
			{
				float databuf[7];
				uint32_t timebuf;

				GetGyroData(&databuf[6],&databuf[0],&databuf[3],&timebuf,0);

				int p;
				for (p = 0; p < N; p++)
				{
				x[p][samplecount] = databuf[p];
				}

				samplecount ++;
				sampled = 0;
			}
		}

		int k;

		for (k = 0;k < N;k++)
		{
			int q;
			float sum = 0;
			for (q = 0; q < numSamples; q++)
			{
				sum += x[k][q];
			}
			xbar[k] = sum/((float)numSamples);
		}

		int i;
		int j;
		int n;

		for (i = 0;i < 3;i++)
		{
			for (j = 0;j < 3;j++)
			{
				float total = 0;
				for (n = 0;n < numSamples;n++)
				{
					total += (x[i][n]-xbar[i])*(x[j][n]-xbar[j]);
				}
				AccNoise[i][j] = total/((float)(numSamples-1));
			}
		}

		for (i = 3;i < 6;i++)
		{
			for (j = 3;j < 6;j++)
			{
				float total = 0;
				for (n = 0;n < numSamples;n++)
				{
					total += (x[i][n]-xbar[i])*(x[j][n]-xbar[j]);
				}
				AngNoise[i-3][j-3] = total/((float)(numSamples-1));
			}
		}
	}
}

void PrintNoise(char * strbuf,float Noise[3][3],int indicator)
{
	if (indicator == Accel_Indicator)
	{
		int i;
		for (i=0;i<3;i++)
		{
			char newstrbuf[256];
			sprintf(newstrbuf,"A %10.5f,%10.5f,%10.5f\r\n",Noise[i][0],Noise[i][1],Noise[i][2]);
			PrintString(newstrbuf);
		}
	}
	else if (indicator == Angular_Indicator)
	{
		int i;
		for (i=0;i<3;i++)
		{
			char newstrbuf[256];
			sprintf(newstrbuf,"W %10.5f,%10.5f,%10.5f\r\n",Noise[i][0],Noise[i][1],Noise[i][2]);
			PrintString(newstrbuf);
		}
	}
}

void SampleCovariance(float GyroCovariance[N][N])
{
	int samplecount = 0;
	float x[N][numSamples];
	float xbar[N];

	while (samplecount < numSamples)
	{
		if (samplecount < numSamples)
		{
			if (sampled == 1)
			{
				float databuf[7];
				uint32_t timebuf;

				GetGyroData(&databuf[6],&databuf[0],&databuf[3],&timebuf,0);

				int p;
				for (p = 0; p < N; p++)
				{
				x[p][samplecount] = databuf[p];
				}

				samplecount ++;
				sampled = 0;
			}
		}

		int k;

		for (k = 0;k < N;k++)
		{
			int q;
			float sum = 0;
			for (q = 0; q < numSamples; q++)
			{
				sum += x[k][q];
			}
			xbar[k] = sum/((float)numSamples);
		}

		int i;
		int j;
		int n;

		for (i = 0;i < N;i++)
		{
			for (j = 0;j < N;j++)
			{
				float total = 0;
				for (n = 0;n < numSamples;n++)
				{
					total += (x[i][n]-xbar[i])*(x[j][n]-xbar[j]);
				}
				GyroCovariance[i][j] = total/((float)(numSamples-1));
			}
		}
	}
}

void PrintGyroCovariance(char * strbuf,float GyroCovariance[N][N])
{
	int i;
//	PrintString("\r\nSensor Covariance Matrix\r\n\r\n");
	for (i=0;i<N;i++)
	{
		char newstrbuf[256];
		sprintf(newstrbuf,"R %10.5f,%10.5f,%10.5f,%10.5f,%10.5f,%10.5f\r\n",GyroCovariance[i][0],GyroCovariance[i][1],GyroCovariance[i][2],GyroCovariance[i][3],GyroCovariance[i][4],GyroCovariance[i][5]);
		PrintString(newstrbuf);
	}
//	PrintString("\r\n\r\n");
}

void MyChipSelect(int chip)
{
	HAL_GPIO_WritePin(GPIOA,GPIO_PIN_4,RESET);
	return;
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
	// Pin change interrupt on PA3 for gyroscope new data

	if (GPIO_Pin == GPIO_PIN_13)
		{
		sampled = 1;
		}

	// Pin change interrupt on PA10 for UV new data - doesn't work due to manufacturer
	if (GPIO_Pin == GPIO_PIN_10)
		{
			uvsampled = 1;
		}
	return;
}

float norm(float * vect)
{
	float total = sqrt(vect[0]*vect[0] + vect[1]*vect[1] + vect[2]*vect[2]);
	return total;
}


//void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
//{
////	Written just for ADC interrupt timer
//
//	if (htim == &htim17)
//	{
//		flag = 1;
//	}
//	if (htim == &htim16)
//	{
//		flag2 = 1;
//	}
//}
/* USER CODE END 4 */

/**
  * @brief  Period elapsed callback in non blocking mode
  * @note   This function is called  when TIM6 interrupt took place, inside
  * HAL_TIM_IRQHandler(). It makes a direct call to HAL_IncTick() to increment
  * a global variable "uwTick" used as application time base.
  * @param  htim : TIM handle
  * @retval None
  */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  /* USER CODE BEGIN Callback 0 */

  /* USER CODE END Callback 0 */
  if (htim->Instance == TIM6) {
    HAL_IncTick();
  }
  /* USER CODE BEGIN Callback 1 */

  /* USER CODE END Callback 1 */
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
