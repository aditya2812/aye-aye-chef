#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { AyeAyeStack } from '../lib/aye-aye-stack';

const app = new cdk.App();

new AyeAyeStack(app, 'AyeAyeStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
});