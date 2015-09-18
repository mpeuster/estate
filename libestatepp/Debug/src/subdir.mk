################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
../src/CommunicationManager.cpp \
../src/LocalState.cpp \
../src/StateItem.cpp \
../src/StateManager.cpp \
../src/estatepp.cpp \
../src/util.cpp 

OBJS += \
./src/CommunicationManager.o \
./src/LocalState.o \
./src/StateItem.o \
./src/StateManager.o \
./src/estatepp.o \
./src/util.o 

CPP_DEPS += \
./src/CommunicationManager.d \
./src/LocalState.d \
./src/StateItem.d \
./src/StateManager.d \
./src/estatepp.d \
./src/util.d 


# Each subdirectory must supply rules for building sources it contributes
src/%.o: ../src/%.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: GCC C++ Compiler'
	g++ -D__cplusplus=201103L -O0 -g3 -Wall -c -fmessage-length=0 -std=c++11 -fPIC -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


