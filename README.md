# Tutorial ROS 2

Projeto com os pacotes do tutorial de ROS 2.

## Como clonar e compilar

No seu terminal, execute:

```bash
# 1. Criar o workspace e entrar na pasta src
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# 2. Clonar o repositório

# 3. Voltar para a raiz do workspace e instalar dependências
cd ~/ros2_ws
rosdep install -i --from-paths src --rosdistro $ROS_DISTRO -y

# 4. Compilar o projeto
colcon build

# 5. Carregar o ambiente
source install/setup.bash
