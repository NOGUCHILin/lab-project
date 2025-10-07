# Centralized Port Management Module
# Provides dynamic port configuration and automatic firewall management
{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.portManagement;
  
  # Centralized port definitions
  defaultPorts = {
    codeServer = 8889;
    unifiedDashboard = 3005;
    syncthing = {
      gui = 8384;
      sync = 22000;
      discovery = 21027;
    };
  };
in
{
  options.services.portManagement = {
    enable = mkEnableOption "Centralized port management";
    
    ports = mkOption {
      type = types.attrs;
      default = defaultPorts;
      description = "Central registry of service ports";
    };
    
    autoFirewall = mkOption {
      type = types.bool;
      default = true;
      description = "Automatically open firewall ports for enabled services";
    };
    
    allowedNetworks = mkOption {
      type = types.listOf types.str;
      default = [
        "100.64.0.0/10"    # Tailscale CGNAT
        "192.168.0.0/16"   # Private network class C
        "10.0.0.0/8"       # Private network class A
      ];
      description = "Networks allowed to access services";
    };
    
    useInterfaceRules = mkOption {
      type = types.bool;
      default = false;
      description = "Use interface-specific firewall rules instead of global";
    };
  };
  
  config = mkIf cfg.enable {
    # Export ports for other modules to use
    environment.etc."nixos/ports.json".text = builtins.toJSON cfg.ports;
    
    # Automatically configure firewall based on enabled services
    networking.firewall = mkMerge [
      # Global port configuration (when not using interface rules)
      (mkIf (!cfg.useInterfaceRules && cfg.autoFirewall) {
        allowedTCPPorts = []
          ++ optional (config.services.code-server.enable or false) cfg.ports.codeServer
          ++ optional (config.services.unified-dashboard.enable or false) cfg.ports.unifiedDashboard
          ++ optionals config.services.syncthing.enable [
               cfg.ports.syncthing.sync
               cfg.ports.syncthing.discovery
             ]
          ++ optional config.services.syncthing.enable cfg.ports.syncthing.gui;
        
        allowedUDPPorts = []
          ++ optional config.services.syncthing.enable cfg.ports.syncthing.discovery;
      })
      
      # Interface-specific rules (more secure)
      (mkIf (cfg.useInterfaceRules && cfg.autoFirewall) {
        interfaces = {
          # Tailscale interface
          tailscale0 = {
            allowedTCPPorts = []
              ++ optional (config.services.code-server.enable or false) cfg.ports.codeServer
              ++ optional (config.services.unified-dashboard.enable or false) cfg.ports.unifiedDashboard;
          };
        };
      })
      
      # Network-specific iptables rules for finer control
      (mkIf cfg.autoFirewall {
        extraCommands = ''
          # Function to add rules for a specific port and networks
          add_network_rules() {
            local port=$1
            local protocol=$2
            
            ${concatMapStringsSep "\n" (network: ''
              iptables -I nixos-fw -s ${network} -p $protocol --dport $port -j nixos-fw-accept || true
            '') cfg.allowedNetworks}
          }
          
          # Apply rules for enabled services
          ${optionalString (config.services.code-server.enable or false) ''
            add_network_rules ${toString cfg.ports.codeServer} tcp
          ''}
          
          ${optionalString (config.services.unified-dashboard.enable or false) ''
            add_network_rules ${toString cfg.ports.unifiedDashboard} tcp
          ''}
        '';
        
        extraStopCommands = ''
          # Clean up our custom rules
          ${concatMapStringsSep "\n" (network: ''
            iptables -D nixos-fw -s ${network} -p tcp --dport ${toString cfg.ports.codeServer} -j nixos-fw-accept 2>/dev/null || true
            iptables -D nixos-fw -s ${network} -p tcp --dport ${toString cfg.ports.unifiedDashboard} -j nixos-fw-accept 2>/dev/null || true
          '') cfg.allowedNetworks}
        '';
      })
    ];
    
    # Service configuration helper
    systemd.services.port-registry = {
      description = "Port Registry Service";
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        Type = "oneshot";
        RemainAfterExit = true;
        ExecStart = pkgs.writeShellScript "port-registry" ''
          # Log active ports
          echo "Active service ports:" | ${pkgs.systemd}/bin/systemd-cat -t port-registry
          
          ${optionalString (config.services.code-server.enable or false) ''
            echo "Code Server: ${toString cfg.ports.codeServer}" | ${pkgs.systemd}/bin/systemd-cat -t port-registry
          ''}
          
          ${optionalString (config.services.unified-dashboard.enable or false) ''
            echo "Unified Dashboard: ${toString cfg.ports.unifiedDashboard}" | ${pkgs.systemd}/bin/systemd-cat -t port-registry
          ''}
        '';
      };
    };
    
    # Port conflict detection
    assertions = [
      {
        assertion = cfg.ports.codeServer != cfg.ports.unifiedDashboard;
        message = "Code Server and Unified Dashboard ports must be different";
      }
    ];
  };
}
