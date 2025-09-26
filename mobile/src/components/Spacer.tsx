import * as React from 'react';
import { View } from 'react-native';

export default function Spacer({ h = 12 }: { h?: number }) {
  return <View style={{ height: h }} />;
}
