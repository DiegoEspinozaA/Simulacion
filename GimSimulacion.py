# ~ Simulacion de gimnasio

# ~ Integrantes:
# ~ Diego Espinoza
# ~ Martín Quiroz
# ~ Fabián Vidal
# ~ Italo López

import simpy
import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import scipy.stats as st

# 17:00 - 20:00
TIEMPO_INICIO = 17 * 60
TIEMPO_FIN = 20 * 60 
TIEMPO_ESCOGER_MAQUINA = 2

NUM_MAQUINAS = 10


PROBABILIDAD_USO_MAQUINA = {
	1: 41 / 120,
	2: 34 / 120,
	3: 10 / 120,
	4: 26 / 120,
	5: 30 / 120,
	6: 12 / 120,
	7: 34 / 120,
	8: 20 / 120,
	9: 23 / 120,
	10: 26 / 120,
}

TIEMPO_MEDIO_USO_MAQUINA = {
	1: 55,
	2: 25,
	3: 30,
	4: 25,
	5: 10,
	6: 15,
	7: 30,
	8: 35,
	9: 30,
	10: 12,	
}

VARIANZA_POR_MAQUINA = {
	1: 10,
	2: 8,
	3: 7,
	4: 6,
	5: 5,
	6: 7,
	7: 10,
	8: 12,
	9: 15,
	10: 8,
}


#estadisticas
cantidad_personas = []
tiempo = []
conteos = {
"llega y se va": 0,
}

maquinas = []
conteo_x_maquina = []

personas_ingresaron = []
tiempo_x_persona = []


class Persona:
	def __init__(self, env, nombre, gimnasio):
		self.env = env
		self.gimnasio = gimnasio
		self.nombre = nombre
		self.maquinas_disponibles = self.maquinas()
		self.maquinas_utilizadas = []
		self.tiempo_total = 0
	
		#aqui se genera la probabilidad de uso de cada una de las maquinas. 1, 2, 3 y 4 por separado (no son una rutina)
	def maquinas(self):
		maquinas = []
		#si ingresa al gimnasio esta "obligado" a escoger por lo menos una maquina
		#esto se hace porque en el for que viene en la linea 70 se puede dar el caso que no escoga ninguna maquina
		
		while(len(maquinas) != 1):
			for i in range(NUM_MAQUINAS):
				if random.random() < PROBABILIDAD_USO_MAQUINA[i+1]:
					maquinas.append(i+1)
					break
			
		for i in range(NUM_MAQUINAS):
			if random.random() < PROBABILIDAD_USO_MAQUINA[i+1]:
				if((i+1) not in maquinas):
					maquinas.append(i+1)

		return maquinas

	def escoger_maquina(self):
		#la persona escoge una máquina aleatoria de las disponibles y no utilizadas
		tiempo.append(formato_tiempo(env.now))
		cantidad_personas.append(gimnasio.personas_en_gimnasio)
		maquinas_disponibles_no_utilizadas = [
				maquina for maquina in self.maquinas_disponibles if maquina not in self.maquinas_utilizadas]
		if(len(self.maquinas_disponibles) <= 0 or len(maquinas_disponibles_no_utilizadas) <=0 ):
			print(f'Tiempo {formato_tiempo(env.now)}: {self.nombre} deja el gimnasio, estando un total de: {int(self.tiempo_total)} minutos ->. Personas en el gimnasio: {gimnasio.personas_en_gimnasio}')
			personas_ingresaron.append(self.nombre.split(" ")[1])
			tiempo_x_persona.append(self.tiempo_total)
		else:
			maquina_escogida = random.choice(maquinas_disponibles_no_utilizadas)
			
			if(str(maquina_escogida) not in maquinas):
				maquinas.append(str(maquina_escogida))
				conteo_x_maquina.append(0)
			else:
				conteo_x_maquina[maquinas.index(str(maquina_escogida))] += 1
				
			self.maquinas_utilizadas.append(maquina_escogida)
			print(f'Tiempo {formato_tiempo(env.now)}: {self.nombre} escoge la maquina {maquina_escogida}. Personas en el gimnasio: {self.gimnasio.personas_en_gimnasio}')

			#esperar el tiempo de uso de la máquina
			#tiempo_uso = TIEMPO_USO_MAQUINA[maquina_escogida]
			tiempo_uso = max(0, random.normalvariate(
				TIEMPO_MEDIO_USO_MAQUINA[maquina_escogida], VARIANZA_POR_MAQUINA[maquina_escogida]))
			self.tiempo_total += tiempo_uso
			yield env.timeout(tiempo_uso)

			#si utilizo todas las maquinas del gimnasio la persona se va (editar para que use todas las que eligio en base a las "rutinas mas elegidas")
			if len(self.maquinas_utilizadas) == NUM_MAQUINAS:
				self.maquinas_utilizadas = []
				self.gimnasio.personas_en_gimnasio -= 1
				print(
					f'Tiempo {formato_tiempo(env.now)}: {self.nombre} deja el gimnasio, estando un total de: {int(self.tiempo_total)} minutos ->. Personas en el gimnasio: {gimnasio.personas_en_gimnasio}')
				
			else:
				print(f'Tiempo {formato_tiempo(env.now)}: {self.nombre} deja la maquina {maquina_escogida}. Personas en el gimnasio: {gimnasio.personas_en_gimnasio}')
				# Esperar 2 segundos antes de escoger la siguiente máquina
				espera = max(0, random.normalvariate(TIEMPO_ESCOGER_MAQUINA, 0.5))
				self.tiempo_total += espera
				yield env.timeout(espera)
				if len(self.maquinas_utilizadas) < NUM_MAQUINAS:
					env.process(self.escoger_maquina())


class Gimnasio:
	def __init__(self):
		self.personas_en_gimnasio = 80
		self.limite_personas = 230
		

def formato_tiempo(minutos):
	horas = minutos // 60
	minutos = minutos % 60
	return f'{int(horas):02d}:{int(minutos):02d}'

def retirar_personas(env, gimnasio):
	while True:
		yield env.timeout(20) #se retiran personas de forma aleatoria
		num_personas_retirar = random.randint(1, 3) #determinar el número de personas a retirar (entre 1 y 3)
		#verificar que haya suficientes personas en el gimnasio para retirar
		if gimnasio.personas_en_gimnasio >= num_personas_retirar:
			personas_retirar = random.sample(
				range(1, 60), num_personas_retirar)
			gimnasio.personas_en_gimnasio -= num_personas_retirar

			personas_retiradas = ', '.join(
				[f'Persona {i}' for i in personas_retirar])
			print(f'Tiempo {formato_tiempo(env.now)}: Se retiran {num_personas_retirar} personas del gimnasio: {personas_retiradas}. Personas en el gimnasio: {gimnasio.personas_en_gimnasio}')


def llegada_persona(env, persona, gimnasio):
	#llega al gimnasio y espera antes de escoger la primera máquina
	tiempo.append(formato_tiempo(env.now))
	cantidad_personas.append(gimnasio.personas_en_gimnasio)
	tiempo_llegada = env.now
	if (gimnasio.personas_en_gimnasio + 1 > gimnasio.limite_personas):
		conteos["llega y se va"] += 1
		print(f'Tiempo {formato_tiempo(tiempo_llegada)}: {persona.nombre} llega al gimnasio pero se va sin entrar. Personas en el gimnasio: {gimnasio.personas_en_gimnasio} ')
		
	else:
		
		print(f'Tiempo {formato_tiempo(tiempo_llegada)}: {persona.nombre} llega al gimnasio <-. Personas en el gimnasio: {gimnasio.personas_en_gimnasio} ')
		gimnasio.personas_en_gimnasio += 1

	espera = max(0, random.normalvariate(TIEMPO_ESCOGER_MAQUINA, 0.5))
	yield env.timeout(espera)

	#escoge su primera máquina
	env.process(persona.escoger_maquina())

def medidas_desempeño(personas):
    contador_maquinas = {maquina: 0 for maquina in range(1, NUM_MAQUINAS + 1)}

    for persona in personas:
        for maquina in persona.maquinas_utilizadas:
            contador_maquinas[maquina] += 1

    maquina_mas_utilizada = max(contador_maquinas, key=contador_maquinas.get)
    maquina_menos_utilizada = min(contador_maquinas, key=contador_maquinas.get)

    cantidad_personas_mas_utilizada = contador_maquinas[maquina_mas_utilizada]
    cantidad_personas_menos_utilizada = contador_maquinas[maquina_menos_utilizada]

    return maquina_mas_utilizada, cantidad_personas_mas_utilizada, maquina_menos_utilizada, cantidad_personas_menos_utilizada

def contar_utilizaciones_maquinas(personas):
    contador_maquinas = {maquina: 0 for maquina in range(1, NUM_MAQUINAS + 1)}

    for persona in personas:
        for maquina in persona.maquinas_utilizadas:
            contador_maquinas[maquina] += 1

    return contador_maquinas

def calcular_nivel_confianza(personas, maquina):
    maquina_utilizada = [persona.maquinas_utilizadas.count(maquina) for persona in personas]
    media = np.mean(maquina_utilizada)
    desviacion_estandar = np.std(maquina_utilizada)
    n = len(maquina_utilizada)

    # Calcular el intervalo de confianza del 95%
    z = 1.96  # Valor crítico para un nivel de confianza del 95%
    intervalo_inferior = media - (z * desviacion_estandar / np.sqrt(n))
    intervalo_superior = media + (z * desviacion_estandar / np.sqrt(n))

    return intervalo_inferior, intervalo_superior

def calcular_intervalo_confianza_utilizaciones_maquina(personas, maquina, nivel_confianza=0.95):
    utilizaciones_maquina = sum(maquina in persona.maquinas_utilizadas for persona in personas)
    n = len(personas)
    z = st.norm.ppf(1 - (1 - nivel_confianza) / 2)
    error_estandar = np.sqrt(utilizaciones_maquina * (1 - utilizaciones_maquina / n))
    margen_error = z * error_estandar
    intervalo_confianza = (utilizaciones_maquina - margen_error, utilizaciones_maquina + margen_error)
    return intervalo_confianza
    
env = simpy.Environment(initial_time=TIEMPO_INICIO)
gimnasio = Gimnasio()
personas = [Persona(env, f'Persona {i+1}', gimnasio)
			for i in range(gimnasio.personas_en_gimnasio, gimnasio.personas_en_gimnasio *2)]


tiempo_llegada = 0
for persona in personas:
	#generar un tiempo de llegada aleatorio siguiendo una distribución exponencial
	tiempo_llegada += random.expovariate(1)
	env.process(llegada_persona(env, persona, gimnasio))
	env.run(until=TIEMPO_INICIO + tiempo_llegada)


env.process(retirar_personas(env, gimnasio))#retirar personas cada tanto tiempo
env.run(until=TIEMPO_FIN)

#numero de personas en el gimnasio en cada momento de tiempo: 
plt.plot(tiempo, cantidad_personas)
plt.xlabel('Tiempo')
plt.ylabel('Personas')
plt.title('Ocupacion gimnasio')

plt.xticks([0])
plt.show()

plt.bar(personas_ingresaron, tiempo_x_persona)
plt.xlabel("Personas")
plt.ylabel("Tiempo en el gimnasio (minutos)")
plt.title("Tiempo en el gimnasio por persona")
plt.xticks([])
plt.show()

plt.bar(maquinas, conteo_x_maquina)
plt.xlabel("Maquina")
plt.ylabel("Usos")
plt.title("Usos por maquina")
plt.show()

media = np.mean(tiempo_x_persona)
desviacion_estandar = np.std(tiempo_x_persona)

# Calcular el intervalo de confianza para la media con un nivel de confianza del 95%
nivel_confianza = 0.95
intervalo = stats.t.interval(nivel_confianza, len(tiempo_x_persona)-1, loc=media, scale=desviacion_estandar/np.sqrt(len(tiempo_x_persona)))

print("Duración promedio de la estadía de las personas:", sum(tiempo_x_persona) / len(personas_ingresaron),"[min]")
print(f"Intervalo de confianza del {nivel_confianza*100}% para la media de tiempo de estadía de las personas: {intervalo}")
print("Cantidad de personas que llegan y se retiran sin entrar: ", conteos["llega y se va"])
utilizaciones_maquinas = contar_utilizaciones_maquinas(personas)
for maquina, utilizaciones in utilizaciones_maquinas.items():
    print(f"Máquina {maquina}: {utilizaciones} veces utilizada")

maquina_mas_utilizada, cantidad_personas_mas_utilizada, maquina_menos_utilizada, cantidad_personas_menos_utilizada = medidas_desempeño(personas)
print(f"Máquina más utilizada: {maquina_mas_utilizada} - Cantidad de personas: {cantidad_personas_mas_utilizada}")
print(f"Máquina menos utilizada: {maquina_menos_utilizada} - Cantidad de personas: {cantidad_personas_menos_utilizada}")

maquina_mas_utilizada, cantidad_personas_mas_utilizada, _, _ = medidas_desempeño(personas)
intervalo_inferior, intervalo_superior = calcular_nivel_confianza(personas, maquina_mas_utilizada)
print(f"Nivel de confianza para la máquina {maquina_mas_utilizada}: [{intervalo_inferior}, {intervalo_superior}]")

intervalo_confianza_maquina1 = calcular_intervalo_confianza_utilizaciones_maquina(personas, 1, nivel_confianza=0.95)
print("Intervalo de confianza para la máquina 1:", intervalo_confianza_maquina1)

for i in range(NUM_MAQUINAS):
	intervalo_inferior, intervalo_superior = calcular_nivel_confianza(personas, (i+1))
	print(f"Nivel de confianza para la máquina {(i+1)}: [{intervalo_inferior}, {intervalo_superior}]")
	intervalo_confianza_maquina = calcular_intervalo_confianza_utilizaciones_maquina(personas, (i+1), nivel_confianza=0.95)
	print("Intervalo de confianza para la máquina",(i+1),":", intervalo_confianza_maquina)

	
