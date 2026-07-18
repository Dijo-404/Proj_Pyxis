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
  }, [active, scaleAnims]);

  return (
    <View style={styles.wrapper}>
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
              style={[styles.navItem]}
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
                  size={24}
                  color={isActive ? 'white' : '#999'}
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
    paddingHorizontal: spacing.lg,
    paddingBottom: spacing.md,
    paddingTop: spacing.sm,
    backgroundColor: 'transparent',
  },
  nav: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-around',
    backgroundColor: 'rgba(255, 255, 255, 0.85)',
    backdropFilter: 'blur(20px)',
    borderRadius: 28,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    height: 70,
    borderWidth: 1.5,
    borderColor: 'rgba(0, 0, 0, 0.08)',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.15,
    shadowRadius: 24,
    elevation: 12,
    transform: [{ translateY: -2 }],
  },
  navItem: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.md,
  },
  navItemActive: {},
  navIcon: {
    width: 50,
    height: 50,
    borderRadius: 25,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: 'transparent',
    borderWidth: 2,
    borderColor: '#999',
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
