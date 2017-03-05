from westernomega import app, config
from westernomega.config_helper import ConfigHelper
import platform

if __name__ == '__main__':
    app.run(threaded=True,  host=ConfigHelper.get_config_variable(config, 'flask_tcp_ip', format='yaml')
            , debug=ConfigHelper.get_config_variable(config, 'flask_use_debug', format='yaml'),
            port=int(ConfigHelper.get_config_variable(config, 'flask_tcp_port', format='yaml')))
