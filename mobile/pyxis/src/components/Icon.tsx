/**
 * Central icon component.
 *
 * Primary set is FontAwesome (the "fa" family) so the UI reads as a real
 * product rather than emoji. A few accents use Feather for a lighter,
 * react-icons-style stroke look.
 */

import React from 'react';
import { StyleProp, TextStyle } from 'react-native';
import FontAwesome from 'react-native-vector-icons/FontAwesome';
import Feather from 'react-native-vector-icons/Feather';
import { colors } from '../theme';

export type IconSet = 'fa' | 'feather';

export function Icon({
  name,
  size = 18,
  color = colors.text,
  set = 'fa',
  style,
}: {
  name: string;
  size?: number;
  color?: string;
  set?: IconSet;
  style?: StyleProp<TextStyle>;
}) {
  const Comp = set === 'feather' ? Feather : FontAwesome;
  return <Comp name={name} size={size} color={color} style={style} />;
}

export default Icon;
