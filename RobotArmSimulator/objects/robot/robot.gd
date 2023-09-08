extends Node3D

@export var udpPort: int = 4444

@onready var waist:Arm = $Waist
@onready var arm1:Arm = $Arm1
@onready var arm2:Arm = $Arm2
@onready var wrist:Arm = $Wrist

var server: UDPServer

var torque_waist = 0
var torque_arm_1 = 0
var torque_arm_2 = 0
var torque_wrist = 0
var theta1: float = 0
var theta2: float = 0

func _ready():
	#inizializzazione server
	server = UDPServer.new()
	server.listen(udpPort)

	#abilitazione motori
	$motorBase["motor/enable"] = true
	$motorArm1["motor/enable"] = true
	$motorArm2["motor/enable"] = true
	$motorWrist["motor/enable"] = true
	
	#settaggio motori
	$motorBase.set_param(HingeJoint3D.PARAM_MOTOR_TARGET_VELOCITY,0)
	$motorArm1.set_param(HingeJoint3D.PARAM_MOTOR_TARGET_VELOCITY,0)
	$motorArm2.set_param(HingeJoint3D.PARAM_MOTOR_TARGET_VELOCITY,0)
	$motorWrist.set_param(HingeJoint3D.PARAM_MOTOR_TARGET_VELOCITY,0)
	pass
	
func _physics_process(delta):
	server.poll()
	
	theta1 = atan2(arm2.global_position.z - arm1.global_position.z, arm2.global_position.y - arm1.global_position.y)
	theta2 = (atan2($Arm2/End.global_position.z - arm2.global_position.z, $Arm2/End.global_position.y - arm2.global_position.y) - theta1)
	
#	print("Theta1: ", theta1 * 180 / PI)
#	print("Theta2: ", theta2 * 180 / PI)
#	print($Arm2/End.global_position.z, ", ", $Arm2/End.global_position.y)
#	print("____________________")
	
	if server.is_connection_available():
		var peer: PacketPeerUDP = server.take_connection()
		var packet = peer.get_packet()
		torque_waist = packet.decode_float(0)
		torque_arm_1 = packet.decode_float(4)
		torque_arm_2 = packet.decode_float(8)
		torque_wrist = packet.decode_float(12)
		
		waist.setTorque(torque_waist)
		arm1.setTorque(torque_arm_1)
		arm2.setTorque(torque_arm_2)
		wrist.setTorque(torque_wrist)
		
		var tosend =  PackedFloat32Array()
		tosend.append(delta)
		
		tosend.append(waist.global_rotation.x)
		tosend.append(waist.angular_velocity.x)
		
		tosend.append(theta1)
		tosend.append(arm1.angular_velocity.x)
		
		tosend.append(theta2)
		tosend.append(arm2.angular_velocity.x)
		
		tosend.append(wrist.global_rotation.x)
		tosend.append(wrist.angular_velocity.x)
	
		tosend.append($Arm2/End.global_position.z)
		tosend.append($Arm2/End.global_position.y)
		
		peer.put_var(tosend)
