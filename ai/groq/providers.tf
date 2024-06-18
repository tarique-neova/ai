terraform {
  required_version = ">=1.3.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0.2"
    }
  }
}



# Provider configuration for Azure resources
provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy    = true
      recover_soft_deleted_key_vaults = true
    }
  }

  client_id       = "1a33955b-7df1-4dd6-8cb5-c887254391e0"
  client_secret   = "LdV8Q~vtXp-Tp3vDky-23UOZxE4MiX9Skbn52beH"
  tenant_id       = "4a67a577-1e6a-4fe4-80c7-128ade4e55b1"
  subscription_id = "eb6118df-a08f-4b53-9815-945e78e01aa6"
}