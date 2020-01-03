discovered = [
    {
        "DefaultValue": "1",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:asg",
        "MaxValue": 10000,
        "MinValue": 0,
        "OptionName": "MinSize",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "Any",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:asg",
        "OptionName": "Availability Zones",
        "ValueType": "Scalar",
        "ValueOptions": [
            "Any",
            "Any 1",
            "Any 2",
            "Any 3"
        ]
    },
    {
        "DefaultValue": "4",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:asg",
        "MaxValue": 10000,
        "MinValue": 0,
        "OptionName": "MaxSize",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "360",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:asg",
        "MaxValue": 10000,
        "MinValue": 0,
        "OptionName": "Cooldown",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:asg",
        "OptionName": "Custom Availability Zones",
        "ValueType": "List",
        "ValueOptions": [
            "us-east-1a",
            "us-east-1b",
            "us-east-1c",
            "us-east-1d",
            "us-east-1e",
            "us-east-1f"
        ]
    },
    {
        "Namespace": "aws:autoscaling:launchconfiguration",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "RestartEnvironment",
        "OptionName": "BlockDeviceMappings"
    },
    {
        "DefaultValue": "5 minute",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "OptionName": "MonitoringInterval",
        "ValueType": "Scalar",
        "ValueOptions": [
            "1 minute",
            "5 minute"
        ]
    },
    {
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "MaxValue": 16384,
        "MinValue": 8,
        "OptionName": "RootVolumeSize"
    },
    {
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "MaxValue": 20000,
        "MinValue": 100,
        "OptionName": "RootVolumeIOPS"
    },
    {
        "Namespace": "aws:autoscaling:launchconfiguration",
        "DefaultValue": "tcp,22,22,0.0.0.0/0",
        "ChangeSeverity": "RestartEnvironment",
        "OptionName": "SSHSourceRestriction",
        "ValueType": "Scalar"
    },
    {
        "Namespace": "aws:autoscaling:launchconfiguration",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "RestartEnvironment",
        "OptionName": "SecurityGroups",
        "MaxLength": 200
    },
    {
        "Namespace": "aws:autoscaling:launchconfiguration",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "OptionName": "ImageId",
        "MaxLength": 200
    },
    {
        "DefaultValue": "t1.micro",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration",
        "OptionName": "InstanceType",
        "ValueType": "Scalar",
        "ValueOptions": [
            "t2.micro",
            "t2.small",
            "t2.medium",
            "t2.large",
            "t2.xlarge",
            "t2.2xlarge",
            "m3.medium",
            "m3.large",
            "m3.xlarge",
            "m3.2xlarge",
            "c3.large",
            "c3.xlarge",
            "c3.2xlarge",
            "c3.4xlarge",
            "c3.8xlarge",
            "t1.micro",
            "t2.nano",
            "m1.small",
            "m1.medium",
            "m1.large",
            "m1.xlarge",
            "c1.medium",
            "c1.xlarge",
            "c4.large",
            "c4.xlarge",
            "c4.2xlarge",
            "c4.4xlarge",
            "c4.8xlarge",
            "m2.xlarge",
            "m2.2xlarge",
            "m2.4xlarge",
            "r4.large",
            "r4.xlarge",
            "r4.2xlarge",
            "r4.4xlarge",
            "r4.8xlarge",
            "r4.16xlarge",
            "m4.large",
            "m4.xlarge",
            "m4.2xlarge",
            "m4.4xlarge",
            "m4.10xlarge",
            "m4.16xlarge",
            "cc1.4xlarge",
            "cc2.8xlarge",
            "hi1.4xlarge",
            "hs1.8xlarge",
            "cr1.8xlarge",
            "g2.2xlarge",
            "g2.8xlarge",
            "p2.xlarge",
            "p2.8xlarge",
            "p2.16xlarge",
            "i2.xlarge",
            "i2.2xlarge",
            "i2.4xlarge",
            "i2.8xlarge",
            "i3.large",
            "i3.xlarge",
            "i3.2xlarge",
            "i3.4xlarge",
            "i3.8xlarge",
            "i3.16xlarge",
            "r3.large",
            "r3.xlarge",
            "r3.2xlarge",
            "r3.4xlarge",
            "r3.8xlarge",
            "d2.xlarge",
            "d2.2xlarge",
            "d2.4xlarge",
            "d2.8xlarge",
            "x1.16xlarge",
            "x1.32xlarge",
            "x1e.32xlarge",
            "f1.2xlarge",
            "f1.16xlarge",
            "g3.4xlarge",
            "g3.8xlarge",
            "g3.16xlarge"
        ]
    },
    {
        "Namespace": "aws:autoscaling:launchconfiguration",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "OptionName": "EC2KeyName",
        "MaxLength": 200
    },
    {
        "OptionName": "IamInstanceProfile",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:autoscaling:launchconfiguration"
    },
    {
        "Namespace": "aws:autoscaling:launchconfiguration",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "OptionName": "RootVolumeType",
        "ValueOptions": [
            "standard",
            "gp2",
            "io1"
        ]
    },
    {
        "OptionName": "Recurrence",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction"
    },
    {
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction",
        "MaxValue": 10000,
        "MinValue": 0,
        "OptionName": "DesiredCapacity"
    },
    {
        "Namespace": "aws:autoscaling:scheduledaction",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "Suspend",
        "ValueType": "Boolean"
    },
    {
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction",
        "MaxValue": 10000,
        "MinValue": 0,
        "OptionName": "MinSize"
    },
    {
        "OptionName": "StartTime",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction"
    },
    {
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction",
        "MaxValue": 10000,
        "MinValue": 0,
        "OptionName": "MaxSize"
    },
    {
        "OptionName": "EndTime",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:scheduledaction"
    },
    {
        "DefaultValue": "5",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MaxValue": 600,
        "MinValue": 1,
        "OptionName": "Period",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "1",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MaxLength": 200,
        "OptionName": "UpperBreachScaleIncrement",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "1",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MaxValue": 600,
        "MinValue": 1,
        "OptionName": "EvaluationPeriods",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "2000000",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MinValue": 0,
        "OptionName": "UpperThreshold",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "2000000",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MinValue": 0,
        "OptionName": "LowerThreshold",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "5",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MaxValue": 600,
        "MinValue": 1,
        "OptionName": "BreachDuration",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "-1",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "MaxLength": 200,
        "OptionName": "LowerBreachScaleIncrement",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "NetworkOut",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "OptionName": "MeasureName",
        "ValueType": "Scalar",
        "ValueOptions": [
            "CPUUtilization",
            "NetworkIn",
            "NetworkOut",
            "DiskWriteOps",
            "DiskReadBytes",
            "DiskReadOps",
            "DiskWriteBytes",
            "Latency",
            "RequestCount",
            "HealthyHostCount",
            "UnHealthyHostCount"
        ]
    },
    {
        "DefaultValue": "Average",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "OptionName": "Statistic",
        "ValueType": "Scalar",
        "ValueOptions": [
            "Minimum",
            "Maximum",
            "Sum",
            "Average"
        ]
    },
    {
        "DefaultValue": "Bytes",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:trigger",
        "OptionName": "Unit",
        "ValueType": "Scalar",
        "ValueOptions": [
            "Seconds",
            "Percent",
            "Bytes",
            "Bits",
            "Count",
            "Bytes/Second",
            "Bits/Second",
            "Count/Second",
            "None"
        ]
    },
    {
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "PauseTime"
    },
    {
        "DefaultValue": "Time",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "OptionName": "RollingUpdateType",
        "ValueType": "Scalar",
        "ValueOptions": [
            "Time",
            "Health",
            "Immutable"
        ]
    },
    {
        "OptionName": "RollingUpdateEnabled",
        "ValueType": "Boolean",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate"
    },
    {
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "MaxValue": 9999,
        "MinValue": 0,
        "OptionName": "MinInstancesInService"
    },
    {
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "MaxValue": 10000,
        "MinValue": 1,
        "OptionName": "MaxBatchSize"
    },
    {
        "Namespace": "aws:autoscaling:updatepolicy:rollingupdate",
        "DefaultValue": "PT30M",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "Timeout",
        "ValueType": "Scalar"
    },
    {
        "Namespace": "aws:cloudformation:template:parameter",
        "DefaultValue": "",
        "ChangeSeverity": "RestartApplicationServer",
        "OptionName": "EnvironmentVariables",
        "ValueType": "KeyValueList"
    },
    {
        "Namespace": "aws:cloudformation:template:parameter",
        "DefaultValue": "https://s3.dualstack.us-east-1.amazonaws.com/elasticbeanstalk-env-resources-us-east-1/stalks/eb_python_4.0.1.95.6/lib/hooks.tar.gz",
        "ChangeSeverity": "Unknown",
        "OptionName": "HooksPkgUrl",
        "ValueType": "Scalar"
    },
    {
        "Namespace": "aws:cloudformation:template:parameter",
        "DefaultValue": "http://s3.amazonaws.com/elasticbeanstalk-samples-us-east-1/python-sample-20150402.zip",
        "ChangeSeverity": "Unknown",
        "OptionName": "AppSource",
        "ValueType": "Scalar"
    },
    {
        "Namespace": "aws:cloudformation:template:parameter",
        "DefaultValue": "80",
        "ChangeSeverity": "Unknown",
        "OptionName": "InstancePort",
        "ValueType": "Scalar"
    },
    {
        "OptionName": "AssociatePublicIpAddress",
        "ValueType": "Boolean",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:ec2:vpc"
    },
    {
        "OptionName": "VPCId",
        "ValueType": "Scalar",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:ec2:vpc"
    },
    {
        "OptionName": "Subnets",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:ec2:vpc"
    },
    {
        "OptionName": "ELBSubnets",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:ec2:vpc"
    },
    {
        "Namespace": "aws:ec2:vpc",
        "DefaultValue": "public",
        "ChangeSeverity": "Unknown",
        "OptionName": "ELBScheme",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:application",
        "MaxLength": 200,
        "OptionName": "Application Healthcheck URL",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "7",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:cloudwatch:logs",
        "OptionName": "RetentionInDays",
        "ValueType": "Scalar",
        "ValueOptions": [
            "1",
            "3",
            "5",
            "7",
            "14",
            "30",
            "60",
            "90",
            "120",
            "150",
            "180",
            "365",
            "400",
            "545",
            "731",
            "1827",
            "3653"
        ]
    },
    {
        "Namespace": "aws:elasticbeanstalk:cloudwatch:logs",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "DeleteOnTerminate",
        "ValueType": "Boolean"
    },
    {
        "Namespace": "aws:elasticbeanstalk:cloudwatch:logs",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "StreamLogs",
        "ValueType": "Boolean"
    },
    {
        "Namespace": "aws:elasticbeanstalk:command",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "IgnoreHealthCheck",
        "ValueType": "Boolean"
    },
    {
        "DefaultValue": "AllAtOnce",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:command",
        "OptionName": "DeploymentPolicy",
        "ValueType": "Scalar",
        "ValueOptions": [
            "AllAtOnce",
            "Rolling",
            "RollingWithAdditionalBatch",
            "Immutable"
        ]
    },
    {
        "DefaultValue": "600",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:command",
        "MaxValue": 3600,
        "MinValue": 1,
        "OptionName": "Timeout",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "Percentage",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:command",
        "OptionName": "BatchSizeType",
        "ValueType": "Scalar",
        "ValueOptions": [
            "Percentage",
            "Fixed"
        ]
    },
    {
        "DefaultValue": "100",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:command",
        "MaxValue": 10000,
        "MinValue": 1,
        "OptionName": "BatchSize",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "Normal",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:control",
        "OptionName": "LaunchType",
        "ValueType": "Scalar",
        "ValueOptions": [
            "Migration",
            "Normal"
        ]
    },
    {
        "DefaultValue": "0",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:control",
        "MinValue": 0,
        "OptionName": "LaunchTimeout",
        "ValueType": "Scalar"
    },
    {
        "Namespace": "aws:elasticbeanstalk:control",
        "DefaultValue": "22",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "DefaultSSHPort",
        "ValueType": "Scalar"
    },
    {
        "Namespace": "aws:elasticbeanstalk:control",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "RollbackLaunchOnFailure",
        "ValueType": "Boolean"
    },
    {
        "DefaultValue": "classic",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:environment",
        "OptionName": "LoadBalancerType",
        "ValueType": "Scalar",
        "ValueOptions": [
            "classic",
            "application",
            "network"
        ]
    },
    {
        "DefaultValue": "LoadBalanced",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:elasticbeanstalk:environment",
        "OptionName": "EnvironmentType",
        "ValueType": "Scalar",
        "ValueOptions": [
            "LoadBalanced",
            "SingleInstance"
        ]
    },
    {
        "Namespace": "aws:elasticbeanstalk:environment",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "ServiceRole",
        "MaxLength": 500
    },
    {
        "Namespace": "aws:elasticbeanstalk:environment",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "OptionName": "ExternalExtensionsS3Key",
        "MaxLength": 1024
    },
    {
        "Namespace": "aws:elasticbeanstalk:environment",
        "ValueType": "Scalar",
        "ChangeSeverity": "RestartEnvironment",
        "OptionName": "ExternalExtensionsS3Bucket",
        "MaxLength": 255
    },
    {
        "DefaultValue": "basic",
        "ChangeSeverity": "RestartEnvironment",
        "Namespace": "aws:elasticbeanstalk:healthreporting:system",
        "OptionName": "SystemType",
        "ValueType": "Scalar",
        "ValueOptions": [
            "basic",
            "enhanced"
        ]
    },
    {
        "DefaultValue": "{\"Version\":1,\"CloudWatchMetrics\":{\"Instance\":{\"CPUIrq\":null,\"LoadAverage5min\":null,\"ApplicationRequests5xx\":null,\"ApplicationRequests4xx\":null,\"CPUUser\":null,\"LoadAverage1min\":null,\"ApplicationLatencyP50\":null,\"CPUIdle\":null,\"InstanceHealth\":null,\"ApplicationLatencyP95\":null,\"ApplicationLatencyP85\":null,\"RootFilesystemUtil\":null,\"ApplicationLatencyP90\":null,\"CPUSystem\":null,\"ApplicationLatencyP75\":null,\"CPUSoftirq\":null,\"ApplicationLatencyP10\":null,\"ApplicationLatencyP99\":null,\"ApplicationRequestsTotal\":null,\"ApplicationLatencyP99.9\":null,\"ApplicationRequests3xx\":null,\"ApplicationRequests2xx\":null,\"CPUIowait\":null,\"CPUNice\":null},\"Environment\":{\"InstancesSevere\":null,\"InstancesDegraded\":null,\"ApplicationRequests5xx\":null,\"ApplicationRequests4xx\":null,\"ApplicationLatencyP50\":null,\"ApplicationLatencyP95\":null,\"ApplicationLatencyP85\":null,\"InstancesUnknown\":null,\"ApplicationLatencyP90\":null,\"InstancesInfo\":null,\"InstancesPending\":null,\"ApplicationLatencyP75\":null,\"ApplicationLatencyP10\":null,\"ApplicationLatencyP99\":null,\"ApplicationRequestsTotal\":null,\"InstancesNoData\":null,\"ApplicationLatencyP99.9\":null,\"ApplicationRequests3xx\":null,\"ApplicationRequests2xx\":null,\"InstancesOk\":null,\"InstancesWarning\":null}}}",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:healthreporting:system",
        "MaxLength": 32000,
        "OptionName": "ConfigDocument",
        "ValueType": "Json"
    },
    {
        "DefaultValue": "Ok",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:healthreporting:system",
        "OptionName": "HealthCheckSuccessThreshold",
        "ValueType": "Scalar",
        "ValueOptions": [
            "Ok",
            "Warning",
            "Degraded",
            "Severe"
        ]
    },
    {
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:hostmanager",
        "OptionName": "LogPublicationControl",
        "ValueType": "Boolean",
        "ValueOptions": [
            "true",
            "false"
        ]
    },
    {
        "Namespace": "aws:elasticbeanstalk:managedactions",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "ManagedActionsEnabled",
        "ValueType": "Boolean"
    },
    {
        "Namespace": "aws:elasticbeanstalk:managedactions",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "PreferredStartTime",
        "MaxLength": 9
    },
    {
        "Namespace": "aws:elasticbeanstalk:managedactions:platformupdate",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "InstanceRefreshEnabled",
        "ValueType": "Boolean"
    },
    {
        "Namespace": "aws:elasticbeanstalk:managedactions:platformupdate",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "UpdateLevel",
        "ValueOptions": [
            "patch",
            "minor"
        ]
    },
    {
        "Namespace": "aws:elasticbeanstalk:monitoring",
        "DefaultValue": "true",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "Automatically Terminate Unhealthy Instances",
        "ValueType": "Boolean"
    },
    {
        "DefaultValue": "email",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:sns:topics",
        "OptionName": "Notification Protocol",
        "ValueType": "Scalar",
        "ValueOptions": [
            "http",
            "https",
            "email",
            "email-json",
            "sqs"
        ]
    },
    {
        "OptionName": "Notification Topic Name",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:sns:topics"
    },
    {
        "OptionName": "Notification Endpoint",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:sns:topics"
    },
    {
        "OptionName": "Notification Topic ARN",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elasticbeanstalk:sns:topics"
    },
    {
        "DefaultValue": "false",
        "ChangeSeverity": "RestartApplicationServer",
        "Namespace": "aws:elasticbeanstalk:xray",
        "OptionName": "XRayEnabled",
        "ValueType": "Scalar",
        "ValueOptions": [
            "true",
            "false"
        ]
    },
    {
        "Namespace": "aws:elb:healthcheck",
        "DefaultValue": "TCP:80",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "Target",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "3",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:healthcheck",
        "MaxValue": 10,
        "MinValue": 2,
        "OptionName": "HealthyThreshold",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "5",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:healthcheck",
        "MaxValue": 10,
        "MinValue": 2,
        "OptionName": "UnhealthyThreshold",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "5",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:healthcheck",
        "MaxValue": 60,
        "MinValue": 2,
        "OptionName": "Timeout",
        "ValueType": "Scalar"
    },
    {
        "DefaultValue": "30",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:healthcheck",
        "MaxValue": 300,
        "MinValue": 5,
        "OptionName": "Interval",
        "ValueType": "Scalar"
    },
    {
        "OptionName": "PolicyNames",
        "ValueType": "List",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:elb:listener"
    },
    {
        "DefaultValue": "80",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:elb:listener",
        "MaxValue": 65535,
        "MinValue": 1,
        "OptionName": "InstancePort",
        "ValueType": "Scalar"
    },
    {
        "OptionName": "SSLCertificateId",
        "ValueType": "Scalar",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:elb:listener"
    },
    {
        "Namespace": "aws:elb:listener",
        "ValueType": "Scalar",
        "ChangeSeverity": "Unknown",
        "OptionName": "InstanceProtocol",
        "ValueOptions": [
            "HTTP",
            "TCP",
            "HTTPS",
            "SSL"
        ]
    },
    {
        "Namespace": "aws:elb:listener",
        "DefaultValue": "true",
        "ChangeSeverity": "Unknown",
        "OptionName": "ListenerEnabled",
        "ValueType": "Boolean"
    },
    {
        "DefaultValue": "HTTP",
        "ChangeSeverity": "Unknown",
        "Namespace": "aws:elb:listener",
        "OptionName": "ListenerProtocol",
        "ValueType": "Scalar",
        "ValueOptions": [
            "HTTP",
            "TCP",
            "HTTPS",
            "SSL"
        ]
    },
    {
        "DefaultValue": "HTTPS",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "OptionName": "LoadBalancerSSLPortProtocol",
        "ValueType": "Scalar",
        "ValueOptions": [
            "HTTPS",
            "SSL"
        ]
    },
    {
        "DefaultValue": "OFF",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "OptionName": "LoadBalancerHTTPPort",
        "ValueType": "Scalar",
        "ValueOptions": [
            "OFF",
            "80"
        ]
    },
    {
        "DefaultValue": "HTTP",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "OptionName": "LoadBalancerPortProtocol",
        "ValueType": "Scalar",
        "ValueOptions": [
            "HTTP",
            "TCP"
        ]
    },
    {
        "Namespace": "aws:elb:loadbalancer",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "SSLCertificateId",
        "MaxLength": 200
    },
    {
        "OptionName": "SecurityGroups",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer"
    },
    {
        "Namespace": "aws:elb:loadbalancer",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "CrossZone",
        "ValueType": "Boolean"
    },
    {
        "DefaultValue": "OFF",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer",
        "OptionName": "LoadBalancerHTTPSPort",
        "ValueType": "Scalar",
        "ValueOptions": [
            "OFF",
            "443",
            "8443"
        ]
    },
    {
        "OptionName": "ManagedSecurityGroup",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:loadbalancer"
    },
    {
        "OptionName": "PublicKeyPolicyNames",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies"
    },
    {
        "OptionName": "LoadBalancerPorts",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies"
    },
    {
        "DefaultValue": "60",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "MaxValue": 3600,
        "MinValue": 1,
        "OptionName": "ConnectionSettingIdleTimeout",
        "ValueType": "Scalar"
    },
    {
        "Namespace": "aws:elb:policies",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "ConnectionDrainingEnabled",
        "ValueType": "Boolean"
    },
    {
        "OptionName": "PublicKey",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies"
    },
    {
        "DefaultValue": "20",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "MaxValue": 3600,
        "MinValue": 1,
        "OptionName": "ConnectionDrainingTimeout",
        "ValueType": "Scalar"
    },
    {
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies",
        "MaxValue": 1000000,
        "MinValue": 0,
        "OptionName": "Stickiness Cookie Expiration"
    },
    {
        "OptionName": "InstancePorts",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies"
    },
    {
        "OptionName": "SSLProtocols",
        "ValueType": "CommaSeparatedList",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies"
    },
    {
        "OptionName": "CookieName",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies"
    },
    {
        "OptionName": "SSLReferencePolicy",
        "ValueType": "Scalar",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies"
    },
    {
        "OptionName": "ProxyProtocol",
        "ValueType": "Boolean",
        "ChangeSeverity": "NoInterruption",
        "Namespace": "aws:elb:policies"
    },
    {
        "Namespace": "aws:elb:policies",
        "DefaultValue": "false",
        "ChangeSeverity": "NoInterruption",
        "OptionName": "Stickiness Policy",
        "ValueType": "Boolean"
    }
]