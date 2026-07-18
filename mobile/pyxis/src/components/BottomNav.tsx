import React, { useRef, useEffect } from 'react';
import { Animated, StyleSheet, TouchableOpacity, View } from 'react-native';
import Icon from './Icon';
import { spacing } from '../theme';

type NavItem = 'dashboard' | 'risks' | 'profile';

export default function BottomNav({
  active,
  onPress,
}: {
  active: NavItem;
  onPress: (tab: NavItem) => void;
}) {
  const items: { key: NavItem; icon: string }[] = [
    { key: 'dashboard', icon: 'home' },
    { key: 'risks', icon: 'bar-chart' },
    { key: 'profile', icon: 'user' },
  ];

  const scaleAnims = useRef({
    dashboard: new Animated.Value(0),
    risks: new Animated.Value(0),
    profile: new Animated.Value(0),
  }).current;

  useEffect(() => {
    items.forEach(item => {
      Animated.spring(scaleAnims[item.key], {
        toValue: active === item.key ? 1 : 0,
        useNativeDriver: true,
        friction: 7,
        tension: 40,
      }).start();
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [active]);

  return (
    <View style={styles.wrapper} pointerEvents="box-none">
      <View style={styles.nav}>
        {items.map(item => {
          const isActive = active === item.key;
          const scaleInterpolate = scaleAnims[item.key].interpolate({
            inputRange: [0, 1],
            outputRange: [1, 1.1],
          });

          return (
            <TouchableOpacity
              key={item.key}
              style={styles.navItem}
              activeOpacity={0.8}
              onPress={() => onPress(item.key)}>
              <Animated.View
                style={[
                  styles.navIcon,
                  isActive && styles.navIconActive,
                  {
                    transform: [{ scale: scaleInterpolate }],
                  },
                ]}>
                <Icon
                  name={item.icon}
                  set="feather"
                  size={22}
                  color={isActive ? 'white' : '#9A9A9A'}
                />
              </Animated.View>
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  wrapper: {
    position: 'absolute',
    left: 0,
    right: 0,
    bottom: spacing.lg,
    alignItems: 'center',
  },
  nav: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    alignSelf: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.72)',
    borderRadius: 38,
    paddingHorizontal: spacing.sm,
    height: 68,
    gap: spacing.sm,
    borderWidth: 1.5,
    borderColor: 'rgba(255, 255, 255, 0.6)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.18,
    shadowRadius: 20,
    elevation: 14,
  },
  navItem: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.xs,
  },
  navIcon: {
    width: 46,
    height: 46,
    borderRadius: 23,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
    borderWidth: 1.5,
    borderColor: 'rgba(2, 0, 0, 0.27)',
  },
  navIconActive: {
    backgroundColor: '#000',
    borderColor: '#000',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 6,
  },
});
