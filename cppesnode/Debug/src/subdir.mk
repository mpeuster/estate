################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
CPP_SRCS += \
../src/ZmqServer.cpp \
../src/cppesnode.cpp 

OBJS += \
./src/ZmqServer.o \
./src/cppesnode.o 

CPP_DEPS += \
./src/ZmqServer.d \
./src/cppesnode.d 


# Each subdirectory must supply rules for building sources it contributes
src/%.o: ../src/%.cpp
	@echo 'Building file: $<'
	@echo 'Invoking: GCC C++ Compiler'
	g++ -I"/home/manuel/estate/libestatepp/src" -I/home/manuel/zmqpp/src/zmqpp -O0 -g3 -Wall -c -fmessage-length=0 -std=c++11 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


